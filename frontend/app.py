"""Prévia navegável, isolada do banco real, usando os services existentes."""

from __future__ import annotations

import json
import os
import stat
import sys
import unicodedata
from pathlib import Path

from PyQt6.QtCore import QEvent, QLibraryInfo, QLockFile, QStandardPaths, Qt, QTimer
from PyQt6.QtGui import QColor, QFont, QIcon, QPalette
from PyQt6.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
    QCompleter,
    QDoubleSpinBox,
    QFileDialog,
    QFormLayout,
    QFrame,
    QGroupBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMainWindow,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QSpinBox,
    QStackedWidget,
    QStyle,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

# Running from the source checkout does not require an editable installation.
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backend"))
from planejador.core.exceptions import ErroPlanejamento
from planejador.database import models  # noqa: F401
from planejador.database.connection import Base
from planejador.database.seed import semear
from planejador.services import gerar_plano, listar_protocolos


def label(text: str, size: int = 13, bold: bool = False) -> QLabel:
    widget = QLabel(text)
    widget.setWordWrap(True)
    widget.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Preferred)
    widget.setFont(
        QFont(
            "Helvetica Neue",
            size,
            QFont.Weight.DemiBold if bold else QFont.Weight.Normal,
        )
    )
    widget.setTextFormat(Qt.TextFormat.PlainText)
    return widget


def button(text: str, callback, primary: bool = False) -> QPushButton:
    widget = QPushButton(text)
    widget.setCursor(Qt.CursorShape.PointingHandCursor)
    widget.setMinimumHeight(40)
    widget.setProperty("primary", primary)
    widget.clicked.connect(callback)
    return widget


class SearchableProtocolBox(QComboBox):
    def __init__(self):
        super().__init__()
        self.setEditable(True)
        self.lineEdit().installEventFilter(self)

    def eventFilter(self, watched, event):
        if watched is self.lineEdit() and event.type() == QEvent.Type.MouseButtonPress:
            QTimer.singleShot(0, self.open_search)
        return super().eventFilter(watched, event)

    def open_search(self):
        self.lineEdit().selectAll()
        self.completer().setCompletionPrefix("")
        self.completer().complete()


class ProtocolCompleter(QCompleter):
    def splitPath(self, path):
        return [PlannerWindow.normalized(path)]

    def pathFromIndex(self, index):
        return index.data(Qt.ItemDataRole.DisplayRole)


class PlannerWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Planejador de Experimentos")
        self.resize(1180, 800)
        self.setMinimumSize(880, 640)
        self.engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(self.engine)
        with Session(self.engine) as session:
            semear(session)
            session.commit()
            self.protocols = listar_protocolos(session)
        catalog = json.loads(Path(__file__).with_name("protocolos.json").read_text())
        self.protocols.extend(
            {
                "id": x["id"],
                "nome": x["name"],
                "descricao": f"{x['id']} · {x['status']}\nOrigem: {x['origem']}\nReferências indicadas: {x['source_codes']}\nConsulta ao catálogo: {x['consultado_em']}\n{x['url']}",
            }
            for x in catalog
        )
        self.plan = None
        self.protocol_done = False
        self.ready = False
        shell = QWidget()
        self.setCentralWidget(shell)
        self.analysis = None
        layout = QHBoxLayout(shell)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(216)
        side = QVBoxLayout(sidebar)
        side.setContentsMargins(24, 32, 24, 24)
        side.setSpacing(16)
        side.addWidget(label("PLANEJADOR", 15, True))
        side.addWidget(label("Laboratório\nMicrobiologia", 12))
        self.steps = []
        for index, text in enumerate(
            [
                "01  Início",
                "02  Protocolo",
                "03  Parâmetros",
                "04  Plano",
                "05  Resultados",
            ]
        ):
            item = button(
                text, lambda checked=False, target=index: self.navigate(target)
            )
            item.setCheckable(True)
            # macOS accessibility activates checkable buttons through their state.
            item.toggled.connect(
                lambda checked, target=index: (
                    self.navigate(target)
                    if checked and self.stack.currentIndex() != target
                    else None
                )
            )
            item.setMinimumHeight(42)
            self.steps.append(item)
            side.addWidget(item)
        side.addStretch()
        side.addWidget(label("IC · UNIT\nPrévia de interface", 11))
        layout.addWidget(sidebar)
        self.stack = QStackedWidget()
        layout.addWidget(self.stack, 1)
        self.build_home()
        self.build_protocols()
        self.build_parameters()
        self.build_plan()
        self.analysis_scroll = QScrollArea()
        self.analysis_scroll.setWidgetResizable(True)
        self.stack.addWidget(self.analysis_scroll)
        self.steps[2].setToolTip("Disponível depois de confirmar o protocolo.")
        self.steps[3].setToolTip("Disponível depois de gerar um plano válido.")
        self.steps[4].setToolTip(
            "Registre as medições do experimento após concluir o plano."
        )
        self.ready = True
        self.protocol.currentIndexChanged.connect(self.protocol_changed)
        self.protocol.lineEdit().textEdited.connect(self.protocol_changed)
        for field in [
            *self.fields.values(),
            self.excess,
            *self.solution_fields.values(),
        ]:
            field.valueChanged.connect(self.invalidate_plan)
        self.title.textChanged.connect(self.invalidate_plan)
        self.dilution.toggled.connect(self.invalidate_plan)
        self.new_planning()
        self.show_page(0)

    def page(self, eyebrow, title, subtitle):
        content = QWidget()
        body = QVBoxLayout(content)
        body.setContentsMargins(40, 32, 40, 32)
        body.setSpacing(16)
        body.addWidget(label(eyebrow.upper(), 11, True))
        body.addWidget(label(title, 28, True))
        body.addWidget(label(subtitle, 13))
        body.addSpacing(16)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setWidget(content)
        self.stack.addWidget(scroll)
        return body

    def show_page(self, index):
        if index == 2 and not self.protocol_done:
            return
        if index >= 3 and self.plan is None:
            return
        if index == 4 and self.analysis is None:
            from frontend.analysis import AnalysisWidget

            self.analysis = AnalysisWidget()
            self.analysis.setMinimumHeight(1000)
            self.analysis_scroll.setWidget(self.analysis)
            self.analysis.save_experiment.clicked.connect(self.export_plan)
            self.analysis.back.clicked.connect(lambda: self.show_page(3))
            if self.analysis is not None:
                self.analysis.set_experiment(self.title.text().strip(), self.plan)
        self.stack.setCurrentIndex(index)
        for i, item in enumerate(self.steps):
            item.setEnabled(
                i < 2
                or (i == 2 and self.protocol_done)
                or (i >= 3 and self.plan is not None)
            )
            item.setChecked(i == index)
            item.setFont(
                QFont(
                    "Helvetica Neue",
                    13,
                    QFont.Weight.Bold if i == index else QFont.Weight.Normal,
                )
            )

    def navigate(self, index):
        self.show_page(index)

    def invalidate_plan(self, *_):
        if not self.ready:
            return
        self.plan = None
        self.parameters = {}
        self.result_title.clear()
        self.summary.clear()
        self.table.setRowCount(0)
        self.procedure.clear()
        self.export_status.clear()
        self.export_button.setEnabled(False)
        self.steps[3].setEnabled(False)
        self.steps[4].setEnabled(False)
        if self.analysis is not None:
            self.analysis.clear_experiment()

    def reset_parameters(self):
        self.title.clear()
        for key, value in {
            "n_amostras": 1,
            "n_replicatas": 1,
            "n_controles": 0,
        }.items():
            self.fields[key].setValue(value)
        self.excess.setValue(0)
        self.dilution.setChecked(False)
        for key, value in {
            "conc_inicial": 10,
            "conc_final": 1,
            "volume_final": 10,
        }.items():
            self.solution_fields[key].setValue(value)
        self.error.clear()
        self.invalidate_plan()

    def protocol_changed(self, *_):
        self.protocol_done = False
        self.steps[2].setEnabled(False)
        self.reset_parameters()
        if self.stack.currentIndex() > 1:
            self.show_page(1)

    def new_planning(self):
        self.protocol.setCurrentIndex(-1)
        self.protocol.clearEditText()
        self.protocol_changed()
        self.show_page(1)

    def complete_protocol(self):
        index = self.protocol.findText(
            self.protocol.currentText(), Qt.MatchFlag.MatchExactly
        )
        if index < 0:
            self.description.setText("Selecione um protocolo da lista para continuar.")
            return
        self.protocol.setCurrentIndex(index)
        self.protocol_done = True
        self.show_page(2)

    def build_home(self):
        body = self.page(
            "Seu espaço de trabalho",
            "Da pergunta ao plano experimental.",
            "Organize as variáveis antes de começar a bancada.",
        )
        box = QGroupBox("Seu primeiro planejamento")
        content = QVBoxLayout(box)
        content.setSpacing(16)
        icon = QLabel()
        icon.setPixmap(
            self.style()
            .standardIcon(QStyle.StandardPixmap.SP_FileDialogDetailedView)
            .pixmap(48, 48)
        )
        content.addWidget(icon)
        content.addWidget(label("Comece com um protocolo", 20, True))
        content.addWidget(
            label(
                "Escolha um exemplo, configure o experimento e confira o plano em um só fluxo."
            )
        )
        content.addWidget(button("Novo planejamento", self.new_planning, True))
        body.addWidget(box)
        body.addWidget(label("PRÉVIA DEMONSTRATIVA", 11, True))
        body.addWidget(
            label(
                "Os exemplos usam um banco temporário. Nenhum dado de bancada é alterado. Referências científicas ainda precisam ser vinculadas."
            )
        )
        body.addStretch()

    def build_protocols(self):
        body = self.page(
            "Etapa 1 de 3",
            "Escolha o ponto de partida.",
            "10 candidatos prioritários do catálogo e 2 exemplos demonstrativos.",
        )
        self.protocol = SearchableProtocolBox()
        self.protocol.setMinimumHeight(42)
        self.protocol.setSizeAdjustPolicy(
            QComboBox.SizeAdjustPolicy.AdjustToMinimumContentsLengthWithIcon
        )
        self.protocol.setMinimumContentsLength(16)
        self.protocol.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed
        )
        self.protocol.setEditable(True)
        self.protocol.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)
        self.protocol.lineEdit().setPlaceholderText(
            "Clique e pesquise por nome ou código"
        )
        self.protocol.lineEdit().setClearButtonEnabled(True)
        self.protocol.setAccessibleName("Pesquisar e selecionar protocolo")
        for item in self.protocols:
            text = (
                f"{item['id']} · {item['nome']}"
                if isinstance(item["id"], str)
                else item["nome"]
            )
            self.protocol.addItem(text, item["id"])
            self.protocol.setItemData(
                self.protocol.count() - 1,
                self.normalized(text),
                int(Qt.ItemDataRole.UserRole) + 1,
            )
        completer = ProtocolCompleter(self.protocol.model(), self.protocol)
        completer.setCompletionRole(int(Qt.ItemDataRole.UserRole) + 1)
        completer.setFilterMode(Qt.MatchFlag.MatchContains)
        completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        completer.setCompletionMode(QCompleter.CompletionMode.PopupCompletion)
        self.protocol.setCompleter(completer)
        body.addWidget(label("Protocolo · pesquise neste campo", 12, True))
        body.addWidget(self.protocol)
        self.description = label("")
        box = QGroupBox("Sobre o protocolo selecionado")
        inside = QVBoxLayout(box)
        inside.addWidget(self.description)
        inside.addWidget(
            label(
                "Fonte e versão: ainda não vinculadas no cadastro. Conteúdo demonstrativo, sem liberação para uso em bancada.",
                12,
            )
        )
        body.addWidget(box)
        self.protocol.currentIndexChanged.connect(self.update_protocol)
        self.update_protocol()
        body.addStretch()
        body.addWidget(
            button("Confirmar protocolo e continuar", self.complete_protocol, True)
        )
        body.addWidget(button("Voltar ao início", lambda: self.show_page(0)))

    @staticmethod
    def normalized(text):
        return "".join(
            c
            for c in unicodedata.normalize("NFD", text.casefold())
            if not unicodedata.combining(c)
        )

    def update_protocol(self):
        item = next(
            (x for x in self.protocols if x["id"] == self.protocol.currentData()), None
        )
        self.description.setText(
            (item.get("descricao") or item["nome"])
            if item
            else "Pesquise e selecione um item da lista para continuar."
        )

    def build_parameters(self):
        body = self.page(
            "Etapa 2 de 3",
            "Defina seu experimento.",
            "Os valores são preservados ao voltar entre as etapas.",
        )
        group = QGroupBox("Organização experimental")
        form = QFormLayout(group)
        form.setVerticalSpacing(16)
        form.setHorizontalSpacing(24)
        self.title = QLineEdit("Meu primeiro planejamento")
        self.title.setMaxLength(120)
        form.addRow("Nome do planejamento", self.title)
        self.fields = {}
        for key, text, minimum, value in [
            ("n_amostras", "Amostras", 1, 8),
            ("n_replicatas", "Replicatas por amostra", 1, 3),
            ("n_controles", "Controles (total)", 0, 2),
        ]:
            field = QSpinBox()
            field.setRange(minimum, 10000)
            field.setValue(value)
            self.fields[key] = field
            form.addRow(text, field)
        self.excess = QDoubleSpinBox()
        self.excess.setRange(0, 100)
        self.excess.setValue(10)
        self.excess.setSuffix(" %")
        form.addRow("Margem de excesso", self.excess)
        body.addWidget(group)
        self.dilution = QCheckBox("Incluir preparo por diluição (exemplo numérico)")
        body.addWidget(self.dilution)
        self.solution = QGroupBox("Solução de trabalho · unidades fixas e coerentes")
        sol = QFormLayout(self.solution)
        sol.setVerticalSpacing(16)
        sol.setHorizontalSpacing(24)
        self.solution_fields = {}
        for key, text, value, unit in [
            ("conc_inicial", "Concentração do estoque", 10, " mg/mL"),
            ("conc_final", "Concentração desejada", 1, " mg/mL"),
            ("volume_final", "Volume final total", 10, " mL"),
        ]:
            field = QDoubleSpinBox()
            field.setDecimals(4)
            field.setRange(0.0001, 1000000)
            field.setValue(value)
            field.setSuffix(unit)
            self.solution_fields[key] = field
            sol.addRow(text, field)
        self.solution.setVisible(False)
        self.dilution.toggled.connect(self.solution.setVisible)
        body.addWidget(self.solution)
        self.error = label("")
        self.error.setObjectName("error")
        body.addWidget(self.error)
        body.addWidget(button("Gerar prévia do plano", self.generate, True))
        body.addWidget(button("Voltar ao protocolo", lambda: self.show_page(1)))
        body.addStretch()

    def generate(self):
        self.invalidate_plan()
        self.error.clear()
        if not self.protocol_done:
            self.error.setText("Confirme um protocolo antes de gerar o plano.")
            return
        if self.protocol.currentData() is None:
            self.error.setText("Selecione um protocolo na página Protocolo.")
            return
        if isinstance(self.protocol.currentData(), str):
            self.error.setText(
                f"{self.protocol.currentText()}: incluído no catálogo da interface. Procedimento, materiais e parâmetros específicos aguardam conferência das fontes; cálculo operacional ainda não disponível."
            )
            return
        if not self.title.text().strip():
            self.error.setText("Dê um nome ao planejamento para continuar.")
            self.title.setFocus()
            return
        params = {key: field.value() for key, field in self.fields.items()}
        params["excesso_percentual"] = self.excess.value()
        if self.dilution.isChecked():
            params.update(
                {key: field.value() for key, field in self.solution_fields.items()}
            )
        try:
            with Session(self.engine) as session:
                self.plan = gerar_plano(
                    session, self.protocol.currentData(), **params
                ).como_dict()
        except ErroPlanejamento as exc:
            self.error.setText(f"{exc} {getattr(exc, 'dica', '') or ''}")
            self.solution_fields["conc_final"].setFocus()
            return
        self.export_button.setEnabled(True)
        if self.analysis is not None:
            self.analysis.set_experiment(self.title.text().strip(), self.plan)
        self.parameters = params
        self.result_title.setText(self.title.text().strip())
        self.summary.setText(
            f"{self.plan['protocolo']}\n{self.plan['n_amostras']} amostras · {self.plan['n_replicatas']} replicatas · {self.plan['n_controles']} controles · {self.plan['n_reacoes']} reações"
        )
        items = [
            (kind, item)
            for kind in ["reagentes", "materiais"]
            for item in self.plan[kind]
        ]
        self.table.setRowCount(len(items))
        for row, (kind, item) in enumerate(items):
            for col, value in enumerate(
                [
                    item["nome"],
                    kind.capitalize(),
                    f"{item['quantidade_total']:.4g}",
                    item["unidade"],
                ]
            ):
                self.table.setItem(row, col, QTableWidgetItem(str(value)))
        self.procedure.setText(
            "\n\n".join(
                f"{i + 1}. {step}" for i, step in enumerate(self.plan["procedimento"])
            )
        )
        self.export_status.clear()
        self.show_page(3)

    def build_plan(self):
        body = self.page(
            "Etapa 3 de 3",
            "Confira antes de executar.",
            "Prévia calculada pelo backend. Os exemplos ainda não têm referência científica vinculada.",
        )
        self.result_title = label("", 20, True)
        body.addWidget(self.result_title)
        self.summary = label("")
        body.addWidget(self.summary)
        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(
            ["Item", "Categoria", "Quantidade", "Unidade"]
        )
        self.table.horizontalHeader().setSectionResizeMode(
            0, QHeaderView.ResizeMode.Stretch
        )
        self.table.verticalHeader().hide()
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setMinimumHeight(210)
        body.addWidget(self.table)
        body.addWidget(
            label(
                "Quantidades do cadastro de exemplo: materiais indivisíveis ainda podem aparecer fracionados. Esta prévia não é uma lista de compra validada.",
                12,
            )
        )
        body.addWidget(label("Organização e procedimento", 16, True))
        self.procedure = label("")
        body.addWidget(self.procedure)
        self.export_button = button("Exportar prévia em JSON", self.export_plan)
        self.export_button.setEnabled(False)
        body.addWidget(self.export_button)
        body.addWidget(
            button(
                "Continuar: registrar medições e analisar",
                lambda: self.show_page(4),
                True,
            )
        )
        self.export_status = label("")
        body.addWidget(self.export_status)
        body.addWidget(button("Editar parâmetros", lambda: self.show_page(2)))
        body.addStretch()

    def export_plan(self):
        if self.plan is None:
            return
        path, _ = QFileDialog.getSaveFileName(
            self, "Exportar prévia", "planejamento-previa.json", "JSON (*.json)"
        )
        if not path:
            return
        try:
            self.write_export(Path(path))
        except OSError as exc:
            self.export_status.setText(f"Não foi possível salvar: {exc}")
            return
        self.export_status.setText(f"Prévia exportada: {Path(path).name}")

    def write_export(self, path):
        if self.plan is None:
            raise ValueError("Gere um plano válido antes de exportar.")
        payload = {
            "titulo": self.title.text().strip(),
            "demonstrativo": True,
            "fonte_cientifica": None,
            "unidades_preparo": {"concentracao": "mg/mL", "volume": "mL"},
            "parametros": self.parameters,
            "plano": self.plan,
        }
        if self.analysis is not None and self.analysis.report is not None:
            payload["resultados_observados"] = {
                "medicoes": self.analysis.read_groups(),
                "unidade": self.analysis.unit.text().strip(),
                "analise": self.analysis.report,
            }
        path.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8"
        )


def create_app():
    # macOS file providers mark Qt plugins hidden; Qt skips hidden plugins.
    # Only clear that flag on this installation's plugin files, not user data.
    if sys.platform == "darwin":
        plugins = Path(QLibraryInfo.path(QLibraryInfo.LibraryPath.PluginsPath))
        for plugin in plugins.rglob("*.dylib"):
            flags = plugin.stat().st_flags
            if flags & stat.UF_HIDDEN:
                os.chflags(plugin, flags & ~stat.UF_HIDDEN)
    app = QApplication.instance() or QApplication(sys.argv)
    app.setApplicationName("Planejador de Experimentos")
    app.setApplicationDisplayName("Planejador de Experimentos")
    app.setOrganizationName("Lucas Montalvão")
    icon = Path(__file__).with_name("assets") / "app.png"
    if icon.is_file():
        app.setWindowIcon(QIcon(str(icon)))
    app.setStyle("Fusion")
    palette = QPalette()
    # EXCEPTION to token/css: Qt uses semantic QPalette roles, not CSS HSL channels.
    for role, color in [
        (QPalette.ColorRole.Window, "whitesmoke"),
        (QPalette.ColorRole.Base, "white"),
        (QPalette.ColorRole.WindowText, "black"),
        (QPalette.ColorRole.Text, "black"),
        (QPalette.ColorRole.Button, "white"),
        (QPalette.ColorRole.ButtonText, "black"),
        (QPalette.ColorRole.Highlight, "darkslategray"),
        (QPalette.ColorRole.HighlightedText, "white"),
    ]:
        palette.setColor(role, QColor(color))
    palette.setColor(
        QPalette.ColorGroup.Disabled, QPalette.ColorRole.ButtonText, QColor("gray")
    )
    app.setPalette(palette)
    app.setFont(QFont("Helvetica Neue", 13))
    app.setStyleSheet("""
        QFrame#sidebar { background: palette(base); border-right: 1px solid palette(mid); }
        QGroupBox { background: palette(base); border: 1px solid palette(mid); border-radius: 8px; margin-top: 16px; padding: 24px; }
        QGroupBox::title { subcontrol-origin: margin; left: 16px; }
        QPushButton { padding: 8px 16px; border: 1px solid palette(mid); border-radius: 6px; }
        QPushButton[primary="true"] { background: palette(highlight); color: palette(highlighted-text); }
        QPushButton:checked { background: palette(highlight); color: palette(highlighted-text); }
        QPushButton:focus, QLineEdit:focus, QComboBox:focus { border: 2px solid palette(highlight); }
        QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox { padding: 8px; min-height: 20px; }
        QLabel#error { font-weight: bold; }
        QTableWidget { background: palette(base); gridline-color: palette(mid); }
    """)
    return app


def main():
    app = create_app()
    app.setApplicationName("Planejador de Experimentos")
    lock = QLockFile(
        str(
            Path(
                QStandardPaths.writableLocation(
                    QStandardPaths.StandardLocation.TempLocation
                )
            )
            / "lucas-planejador-experimentos.lock"
        )
    )
    if not lock.tryLock(100):
        print("O Planejador já está aberto. Use a janela existente.")
        return
    window = PlannerWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
