"""Fluxo desktop de planejamento, medições, análise e histórico local."""

from __future__ import annotations

import copy
import json
import os
import stat
import sys
import unicodedata
from datetime import datetime
from html import escape
from pathlib import Path

from PyQt6.QtCore import QEvent, QLibraryInfo, QLockFile, QStandardPaths, Qt, QTimer
from PyQt6.QtGui import QColor, QFont, QIcon, QPalette
from PyQt6.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
    QCompleter,
    QDialog,
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
    QStackedWidget,
    QStyle,
    QTableWidget,
    QTableWidgetItem,
    QTextBrowser,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from frontend.numeric import DecimalSpinBox as QDoubleSpinBox
from frontend.numeric import IntegerSpinBox as QSpinBox

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
            "Segoe UI" if sys.platform == "win32" else "Helvetica Neue",
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
        catalog = json.loads(
            Path(__file__).with_name("protocolos.json").read_text(encoding="utf-8")
        )
        self.catalog = {item["id"]: item for item in catalog}
        self.protocols.extend(
            {
                "id": x["id"],
                "nome": x["name"],
                "descricao": f"{x['id']} · {x['status']}\nOrigem: {x['origem']}\nReferências indicadas: {x['source_codes']}\nConsulta ao catálogo: {x['consultado_em']}\n{x['url']}",
            }
            for x in catalog
        )
        self.protocols = [
            item for item in self.protocols if str(item["id"]).startswith("PREP-")
        ]
        self.plan = None
        self.protocol_done = False
        self.ready = False
        from planejador.services.historico import Historico

        data_dir = Path(
            os.environ.get("PLANEJADOR_DATA_DIR")
            or QStandardPaths.writableLocation(
                QStandardPaths.StandardLocation.AppDataLocation
            )
        )
        archive_directory = None
        if getattr(sys, "frozen", False) and not os.environ.get("PLANEJADOR_DATA_DIR"):
            archive_base = (
                Path(sys.executable).parents[3]
                if sys.platform == "darwin"
                else Path(sys.executable).parent
            )
            archive_directory = archive_base / "Registros de Experimentos"
        self.history = Historico(data_dir, archive_directory)
        self.history_id = None
        self.observation_pending = None
        self.observation_timer = QTimer(self)
        self.observation_timer.setSingleShot(True)
        self.observation_timer.setInterval(400)
        self.observation_timer.timeout.connect(self.save_observations)
        shell = QWidget()
        self.setCentralWidget(shell)
        self.analysis = None
        self.percent_results = None
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
        side.addWidget(label("IC · UNIT\nPlanejamento experimental", 11))
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
        if index == 4 and self.plan.get("pendente", False):
            return
        if index == 4 and self.plan.get("tipo_calculo") in {
            "percentual",
            "molar",
            "estoque",
            "diluicao",
            "seriada",
            "fator",
            "volume",
            "formula",
            "desidratado",
            "recipientes",
        }:
            from frontend.preparos import PreparoResults

            if self.percent_results is None:
                self.percent_results = PreparoResults(
                    self.selected_pop(), self.parameters
                )
                self.analysis_scroll.setWidget(self.percent_results)
                self.percent_results.back.clicked.connect(lambda: self.show_page(3))
                self.percent_results.save.clicked.connect(self.export_plan)
                self.percent_results.updated.connect(self.accept_percent_result)
                self.percent_results.invalid.connect(self.invalidate_plan)
                from frontend.analysis import AnalysisWidget

                self.analysis = AnalysisWidget()
                self.analysis.layout().setContentsMargins(0, 16, 0, 0)
                self.configure_analysis()
                self.analysis.back.hide()
                self.analysis.save_experiment.hide()
                group = QGroupBox("Medições observadas e análise estatística")
                group.setProperty("foldable", True)
                group.setCheckable(True)
                group.setChecked(False)
                group.setMaximumHeight(group.fontMetrics().height() + 20)
                group.toggled.connect(
                    lambda on: group.setMaximumHeight(
                        16777215 if on else group.fontMetrics().height() + 20
                    )
                )
                QVBoxLayout(group).addWidget(self.analysis)
                self.analysis.hide()
                group.toggled.connect(self.analysis.setVisible)
                self.observations_group = group
                result_layout = self.percent_results.layout()
                result_layout.insertWidget(
                    result_layout.indexOf(self.percent_results.back), group
                )
        elif index == 4 and self.analysis is None:
            from frontend.analysis import AnalysisWidget

            self.analysis = AnalysisWidget()
            self.analysis.setMinimumHeight(1000)
            self.analysis_scroll.setWidget(self.analysis)
            self.configure_analysis()
        self.stack.setCurrentIndex(index)
        for i, item in enumerate(self.steps):
            item.setEnabled(
                i < 2
                or (i == 2 and self.protocol_done)
                or (i == 3 and self.plan is not None)
                or (
                    i == 4
                    and self.plan is not None
                    and not self.plan.get("pendente", False)
                )
            )
            item.setChecked(i == index)
            item.setFont(
                QFont(
                    "Segoe UI" if sys.platform == "win32" else "Helvetica Neue",
                    13,
                    QFont.Weight.Bold if i == index else QFont.Weight.Normal,
                )
            )

    def configure_analysis(self):
        self.analysis.set_experiment(self.title.text().strip(), self.plan)
        self.analysis.save_experiment.clicked.connect(self.export_plan)
        self.analysis.back.clicked.connect(lambda: self.show_page(3))
        self.analysis.changed.connect(self.queue_observations)

    def queue_observations(self):
        if (
            self.plan is not None
            and self.analysis is not None
            and self.analysis.context is not None
        ):
            self.observation_pending = (
                copy.deepcopy(self.export_payload()),
                self.history_id,
            )
            self.observation_timer.start()

    def save_observations(self):
        if self.observation_pending is None:
            return True
        if not self.save_history(self.observation_pending):
            return False
        self.observation_pending = None
        self.pending_export.hide()
        return True

    def flush_observations(self):
        self.observation_timer.stop()
        return self.save_observations()

    def closeEvent(self, event):
        if not self.flush_observations():
            event.ignore()
            self.show_pending_data()
            return
        super().closeEvent(event)

    def show_pending_data(self):
        self.show_page(0)
        QTimer.singleShot(
            0,
            lambda: self.stack.widget(0).ensureWidgetVisible(
                self.pending_export, 0, 24
            ),
        )

    def export_pending(self):
        if self.observation_pending is None:
            return
        path, _ = QFileDialog.getSaveFileName(
            self,
            "Salvar dados pendentes",
            str(self.history.archive_dir / "experimento-pendente.json"),
            "JSON (*.json)",
        )
        if not path:
            return
        try:
            Path(path).write_text(
                json.dumps(
                    {
                        "consulta_apenas": True,
                        "experimento": self.observation_pending[0],
                    },
                    ensure_ascii=False,
                    indent=2,
                    allow_nan=False,
                ),
                encoding="utf-8",
            )
        except (OSError, ValueError) as exc:
            self.history_status.setText(
                f"Não foi possível exportar. Os dados continuam em memória: {exc}"
            )
            return
        self.observation_timer.stop()
        self.observation_pending = None
        self.pending_export.hide()
        self.history_status.setText(
            f"Cópia de consulta salva em {path}. O histórico não foi atualizado; preserve esse arquivo."
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
        self.percent_form.blockSignals(True)
        self.percent_form.set_protocol_type("percentual")
        self.percent_form.set_values(
            {
                "base": "m/v",
                "soluto": "",
                "solvente": "",
                "concentracao": 0,
                "quantidade_final": 0,
                "pureza": 0,
            }
        )
        self.percent_form.blockSignals(False)
        if self.percent_results is not None:
            self.analysis_scroll.takeWidget().deleteLater()
            self.percent_results = None
            self.analysis = None
        self.error.clear()
        self.invalidate_plan()

    def protocol_changed(self, *_):
        if not self.flush_observations():
            self.protocol.blockSignals(True)
            self.protocol.setCurrentIndex(
                self.protocol.findData(self.observation_pending[0]["protocolo_id"])
            )
            self.protocol.blockSignals(False)
            self.show_pending_data()
            return
        self.history_id = None
        self.protocol_done = False
        self.steps[2].setEnabled(False)
        self.reset_parameters()
        if self.stack.currentIndex() > 1:
            self.show_page(1)

    def new_planning(self):
        if not self.flush_observations():
            self.show_pending_data()
            return
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
        if not self.title.text().strip():
            self.title.setText(self.protocol.currentText())
        operational = bool(
            self.selected_pop() and self.selected_pop().get("tipo_calculo")
        )
        if operational:
            self.percent_form.set_protocol_type(self.selected_pop()["tipo_calculo"])
        self.percent_form.setVisible(operational)
        self.generic_parameters.setVisible(
            not isinstance(self.protocol.currentData(), str)
        )
        self.dilution.setVisible(not isinstance(self.protocol.currentData(), str))
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
                "Escolha um protocolo, configure o experimento e confira os resultados do planejamento."
            )
        )
        content.addWidget(button("Novo planejamento", self.new_planning, True))
        body.addWidget(box)
        body.addWidget(label("Histórico de experimentos", 18, True))
        self.history_table = QTableWidget(0, 3)
        self.history_table.setHorizontalHeaderLabels(
            ["Planejamento", "Consultar", "Arquivar"]
        )
        self.history_table.horizontalHeader().setSectionResizeMode(
            0, QHeaderView.ResizeMode.Stretch
        )
        self.history_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.history_table.setColumnWidth(1, 130)
        self.history_table.setColumnWidth(2, 130)
        self.history_table.verticalHeader().setDefaultSectionSize(46)
        self.history_table.verticalHeader().hide()
        self.history_table.setMaximumHeight(330)
        body.addWidget(self.history_table)
        self.history_empty = label("Nenhum experimento salvo ainda.")
        body.addWidget(self.history_empty)
        self.history_status = label("")
        body.addWidget(self.history_status)
        self.pending_export = button(
            "Exportar dados ainda não salvos", self.export_pending
        )
        self.pending_export.hide()
        body.addWidget(self.pending_export)
        self.history_retry = button("Tentar salvar novamente", self.retry_history)
        self.history_retry.hide()
        body.addWidget(self.history_retry)
        self.history_details = QGroupBox("Detalhes técnicos")
        self.history_details.setCheckable(True)
        self.history_details.setStyleSheet(
            "QGroupBox { background: palette(window); border: none; padding: 0; margin-top: 20px; } QGroupBox::title { left: 0; }"
        )
        self.history_details.setChecked(False)
        self.history_error_text = QTextEdit()
        self.history_error_text.setReadOnly(True)
        self.history_error_text.setMaximumHeight(120)
        history_details_layout = QVBoxLayout(self.history_details)
        history_details_layout.setContentsMargins(0, 4, 0, 0)
        history_details_layout.addWidget(self.history_error_text)
        self.history_error_text.hide()
        self.history_details.toggled.connect(self.history_error_text.setVisible)
        self.history_details.hide()
        body.addWidget(self.history_details)
        body.addWidget(
            button("Consultar registros arquivados", self.open_archived_record)
        )
        body.addWidget(
            label(
                f"Até 10 experimentos recentes. Os itens retirados são preservados para consulta e exportação em: {self.history.archive_dir}",
                11,
            )
        )
        self.refresh_history()
        body.addWidget(label("PLANEJAMENTO EXPERIMENTAL", 11, True))
        body.addWidget(
            label(
                "Os cálculos são dimensionamentos planejados. Confira a fonte, as condições do protocolo e os requisitos do seu experimento."
            )
        )
        body.addStretch()

    def refresh_history(self):
        records = self.history.list()
        self.history_table.setVisible(bool(records))
        self.history_empty.setVisible(not records)
        self.history_table.setMaximumHeight(min(330, 36 + 46 * len(records)))
        self.history_table.setRowCount(len(records))
        for row, record in enumerate(records):
            payload = json.loads(record["conteudo"])
            self.history_table.setItem(
                row, 0, QTableWidgetItem(payload.get("titulo", "Sem título"))
            )
            self.history_table.setCellWidget(
                row,
                1,
                button(
                    "Consultar",
                    lambda checked=False, data=payload: self.view_record(data),
                ),
            )
            self.history_table.setCellWidget(
                row,
                2,
                button(
                    "Arquivar",
                    lambda checked=False, rid=record["id"]: self.archive_record(rid),
                ),
            )

    def archive_record(self, record_id):
        if record_id == self.history_id and not self.flush_observations():
            self.show_pending_data()
            return
        try:
            target = self.history.archive(record_id)
        except (OSError, ValueError, SQLAlchemyError) as exc:
            self.show_history_error(
                "Não foi possível arquivar. O registro foi preservado.", exc
            )
            return
        if record_id == self.history_id:
            self.history_id = None
        self.history_status.setText(f"Arquivado para consulta: {target.name}")
        self.refresh_history()

    def view_record(self, payload):
        dialog = QDialog(self)
        dialog.setWindowTitle("Consulta do experimento")
        dialog.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        dialog.resize(720, 600)
        layout = QVBoxLayout(dialog)
        text = QTextEdit()
        text.setReadOnly(True)
        data = payload.get("experimento", payload)
        plan = data.get("plano", {})
        params = data.get("parametros", {})
        lines = [
            data.get("titulo", "Experimento"),
            plan.get("protocolo", ""),
            "",
            "Parâmetros informados",
        ]
        lines += [
            f"{key.replace('_', ' ').capitalize()}: {value}"
            for key, value in params.items()
        ]
        lines += ["", "Resultado do planejamento"]
        for item in plan.get("reagentes", []):
            lines.append(
                f"{item['nome']}: {item['quantidade_total']} {item['unidade']}"
            )
        lines += [plan.get("solvente", ""), "", "Procedimento"] + plan.get(
            "procedimento", []
        )
        if plan.get("erros_rotulo"):
            lines += ["", "Dados opcionais do rótulo a conferir"] + list(
                plan["erros_rotulo"].values()
            )
        lines += ["", "Fontes"] + [
            f"{source.get('title', '')} — {source.get('url', '')}"
            for source in plan.get("fontes", [])
        ]
        if data.get("resultados_observados"):
            lines += [
                "",
                "Medições e análise observadas",
                json.dumps(data["resultados_observados"], ensure_ascii=False, indent=2),
            ]
        text.setPlainText("\n".join(lines))
        layout.addWidget(text)
        status = label(
            "Consulta somente leitura. Este registro não reabre o planejamento."
        )
        layout.addWidget(status)

        def export():
            path, _ = QFileDialog.getSaveFileName(
                dialog, "Exportar registro", "experimento.json", "JSON (*.json)"
            )
            if path:
                try:
                    Path(path).write_text(
                        json.dumps(
                            payload, ensure_ascii=False, indent=2, allow_nan=False
                        ),
                        encoding="utf-8",
                    )
                except (OSError, ValueError) as exc:
                    status.setText(f"Não foi possível exportar: {exc}")
                    return
                status.setText("Registro exportado.")

        layout.addWidget(button("Exportar registro em JSON", export))
        layout.addWidget(button("Fechar consulta", dialog.accept))
        dialog.open()

    def open_archived_record(self):
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Consultar registro arquivado",
            str(self.history.archive_dir),
            "JSON (*.json)",
        )
        if not path:
            return
        try:
            target = Path(path)
            if target.stat().st_size > 10_000_000:
                raise ValueError("Arquivo maior que o limite de consulta de 10 MB.")
            payload = json.loads(target.read_text(encoding="utf-8"))
            if not isinstance(payload, dict) or not isinstance(
                payload.get("experimento"), dict
            ):
                raise ValueError(
                    "O arquivo não contém um registro de experimento arquivado."
                )
        except (OSError, ValueError) as exc:
            self.history_status.setText(f"Não foi possível consultar: {exc}")
            return
        self.view_record(payload)

    def retry_history(self):
        if self.flush_observations():
            self.history_status.setText("Planejamento salvo no histórico.")

    def show_history_error(self, message, exc):
        self.history_status.setText(message)
        self.history_error_text.setPlainText(
            f"{type(exc).__name__}: {getattr(exc, 'orig', exc)}"
        )
        self.history_details.setChecked(False)
        self.history_error_text.hide()
        self.history_details.show()
        self.history_retry.setVisible(self.observation_pending is not None)

    def save_history(self, snapshot=None):
        payload, record_id = (
            snapshot
            if snapshot is not None
            else (self.export_payload(), self.history_id)
        )
        try:
            self.history_id = self.history.save(payload, record_id)
        except (OSError, ValueError, SQLAlchemyError) as exc:
            self.observation_pending = (copy.deepcopy(payload), record_id)
            self.pending_export.show()
            self.show_history_error(
                "Não foi possível salvar. Os dados continuam em memória. Em Início, tente novamente ou salve uma cópia antes de fechar.",
                exc,
            )
            self.export_status.setText(self.history_status.text())
            if self.analysis is not None and self.analysis.context is not None:
                self.analysis.status.setText(self.history_status.text())
            return False
        self.history_status.clear()
        self.history_details.hide()
        self.history_retry.hide()
        try:
            self.refresh_history()
        except (OSError, ValueError, SQLAlchemyError) as exc:
            self.show_history_error(
                "Dados salvos. Não foi possível atualizar a lista do histórico.", exc
            )
        return True

    def build_protocols(self):
        body = self.page(
            "Etapa 1 de 3",
            "Escolha o ponto de partida.",
            "Dez protocolos PREP. A situação de implementação e as fontes aparecem em cada ficha.",
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
        self.description = label("", 16, True)
        self.protocol_purpose = label("")
        box = QGroupBox("Sobre este protocolo")
        inside = QVBoxLayout(box)
        inside.setSpacing(8)
        inside.addWidget(self.description)
        inside.addWidget(self.protocol_purpose)
        body.addWidget(box)
        self.protocol_sources = QGroupBox("Fontes e rastreabilidade")
        self.protocol_sources.setCheckable(True)
        self.protocol_sources.setStyleSheet(
            "QGroupBox { background: palette(window); border: none; padding: 0; margin-top: 20px; } QGroupBox::title { left: 0; }"
        )
        self.protocol_sources.setChecked(False)
        self.protocol_source_text = QTextBrowser()
        self.protocol_source_text.setOpenExternalLinks(True)
        self.protocol_source_text.setMaximumHeight(230)
        protocol_sources_layout = QVBoxLayout(self.protocol_sources)
        protocol_sources_layout.setContentsMargins(0, 4, 0, 0)
        protocol_sources_layout.addWidget(self.protocol_source_text)
        self.protocol_source_text.hide()
        self.protocol_sources.toggled.connect(self.protocol_source_text.setVisible)
        body.addWidget(self.protocol_sources)
        self.preview_button = button("Ver POP", self.preview_pop)
        self.docx_button = button("Gerar DOCX do POP", self.export_pop)
        body.addWidget(self.preview_button, alignment=Qt.AlignmentFlag.AlignLeft)
        body.addWidget(self.docx_button, alignment=Qt.AlignmentFlag.AlignLeft)
        self.pop_status = label("")
        body.addWidget(self.pop_status)
        self.protocol.currentIndexChanged.connect(self.update_protocol)
        self.protocol.lineEdit().textChanged.connect(self.update_protocol)
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

    def update_protocol(self, *_):
        if (
            not self.protocol.currentText().strip()
            and self.protocol.currentIndex() >= 0
        ):
            self.protocol.setCurrentIndex(-1)
        index = self.protocol.findText(
            self.protocol.currentText(), Qt.MatchFlag.MatchExactly
        )
        selected_id = self.protocol.itemData(index) if index >= 0 else None
        available = self.selected_pop() is not None
        self.preview_button.setEnabled(available)
        self.docx_button.setEnabled(available)
        self.pop_status.clear()
        item = next((x for x in self.protocols if x["id"] == selected_id), None)
        protocol = self.selected_pop()
        self.protocol_sources.setVisible(protocol is not None)
        self.protocol_sources.setChecked(False)
        self.protocol_source_text.hide()
        self.protocol_purpose.clear()
        self.protocol_source_text.clear()
        if protocol:
            from frontend.pop import pop_sections

            self.description.setText(f"{protocol['id']} · {protocol['name']}")
            self.protocol_purpose.setText(
                next(
                    (
                        text
                        for title, text in pop_sections(protocol)
                        if title == "Finalidade"
                    ),
                    "",
                )
            )
            references = []
            for source in protocol.get("fontes", []):
                consulted = datetime.fromisoformat(source["consultado_em"])
                pages = ", ".join(str(page) for page in source.get("paginas", []))
                references.append(
                    f"<p><b>{escape(source['title'])}</b><br>"
                    f"{escape(source['organization'])}, {source['year']} · páginas {pages}<br>"
                    f"Consulta: {consulted.strftime('%d/%m/%Y às %H:%M:%S (UTC%z)')}<br>"
                    f'<a href="{escape(source["url"], quote=True)}">Consultar fonte original</a></p>'
                )
            references.append(
                f"<p><b>Origem no catálogo</b><br>{escape(protocol['origem'])}<br>"
                f"Consulta: {escape(protocol['consultado_em'])}<br>"
                f'<a href="{escape(protocol["url"], quote=True)}">Consultar catálogo</a></p>'
            )
            self.protocol_source_text.setHtml("".join(references))
        else:
            self.description.setText(
                (item.get("descricao") or item["nome"])
                if item
                else "Pesquise e selecione um item da lista para continuar."
            )

    def selected_pop(self):
        index = self.protocol.findText(
            self.protocol.currentText(), Qt.MatchFlag.MatchExactly
        )
        return self.catalog.get(self.protocol.itemData(index)) if index >= 0 else None

    def preview_pop(self):
        protocol = self.selected_pop()
        if protocol is None:
            return
        from frontend.pop import pop_text

        dialog = QDialog(self)
        dialog.setWindowTitle(f"Ver POP · {protocol['id']}")
        dialog.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        dialog.resize(720, 620)
        layout = QVBoxLayout(dialog)
        text = QTextEdit()
        text.setReadOnly(True)
        text.setPlainText(pop_text(protocol))
        layout.addWidget(text)
        status = label("")
        layout.addWidget(status)
        layout.addWidget(
            button(
                "Gerar DOCX do POP", lambda: self.export_pop(protocol, status, dialog)
            )
        )
        layout.addWidget(button("Fechar POP", dialog.accept))
        dialog.open()

    def export_pop(self, protocol=None, status=None, parent=None):
        from frontend.pop import write_pop_docx

        protocol = protocol if isinstance(protocol, dict) else self.selected_pop()
        if protocol is None:
            return
        status = status if status is not None else self.pop_status
        path, _ = QFileDialog.getSaveFileName(
            parent or self,
            "Salvar POP em DOCX",
            f"{protocol['id']}-POP.docx",
            "Documento Word (*.docx)",
        )
        if not path:
            return
        target = Path(path)
        if target.suffix.lower() != ".docx":
            target = target.with_suffix(".docx")
        try:
            write_pop_docx(protocol, target)
        except (OSError, ImportError) as exc:
            status.setText(f"Não foi possível salvar o POP: {exc}")
            return
        status.setText(f"POP salvo: {target.name}")

    def build_parameters(self):
        body = self.page(
            "Etapa 2 de 3",
            "Defina seu experimento.",
            "Os valores são preservados ao voltar entre as etapas.",
        )
        group = QGroupBox("Organização experimental")
        self.generic_parameters = group
        form = QFormLayout(group)
        form.setVerticalSpacing(16)
        form.setHorizontalSpacing(24)
        self.title = QLineEdit("Meu primeiro planejamento")
        self.title.setMaxLength(120)
        body.addWidget(label("Como deseja identificar o planejamento?"))
        body.addWidget(self.title)
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
        from frontend.preparos import PreparoForm

        self.percent_form = PreparoForm()
        self.percent_form.setVisible(False)
        self.percent_form.changed.connect(self.invalidate_plan)
        body.addWidget(self.percent_form)
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
        self.plan_button = button("Seguir para Plano", lambda: self.generate(), True)
        body.addWidget(self.plan_button)
        body.addWidget(button("Voltar ao protocolo", lambda: self.show_page(1)))
        body.addStretch()

    def generate(self):
        if not self.flush_observations():
            self.error.setText(self.history_status.text())
            return
        self.error.clear()
        if not self.protocol_done:
            self.error.setText("Confirme um protocolo antes de gerar o plano.")
            return
        if self.protocol.currentData() is None:
            self.error.setText("Selecione um protocolo na página Protocolo.")
            return
        if not self.title.text().strip():
            self.error.setText("Dê um nome ao planejamento para continuar.")
            self.title.setFocus()
            self.stack.currentWidget().ensureWidgetVisible(self.title)
            return
        params = {key: field.value() for key, field in self.fields.items()}
        params["excesso_percentual"] = self.excess.value()
        if self.dilution.isChecked():
            params.update(
                {key: field.value() for key, field in self.solution_fields.items()}
            )
        pending = False
        protocol = self.selected_pop()
        if protocol and protocol.get("tipo_calculo"):
            from planejador.services.preparos import calcular_preparo

            params = self.percent_form.values()
            try:
                plan = calcular_preparo(protocol, params)
            except ErroPlanejamento as exc:
                self.error.setText(str(exc))
                return
        elif isinstance(self.protocol.currentData(), str):
            self.error.setText(
                "Regras deste protocolo em implantação. Ainda não há cálculo operacional disponível."
            )
            return
        else:
            try:
                with Session(self.engine) as session:
                    plan = gerar_plano(
                        session, self.protocol.currentData(), **params
                    ).como_dict()
            except ErroPlanejamento as exc:
                self.error.setText(f"{exc} {getattr(exc, 'dica', '') or ''}")
                self.solution_fields["conc_final"].setFocus()
                self.stack.currentWidget().ensureWidgetVisible(self.error)
                return
        self.invalidate_plan()
        if self.percent_results is not None:
            self.analysis_scroll.takeWidget().deleteLater()
            self.percent_results = None
            self.analysis = None
        self.plan = plan
        self.continue_button.setEnabled(not pending)
        self.export_button.setEnabled(True)
        if self.analysis is not None and not pending and "resultado" not in plan:
            self.analysis.set_experiment(self.title.text().strip(), self.plan)
        self.parameters = params
        self.render_plan()
        self.save_history()
        self.show_page(3)

    def render_plan(self):
        self.result_title.setText(self.title.text().strip())
        if self.plan.get("tipo_calculo") == "formula":
            r = self.plan["resultado"]
            pending = " ".join(self.plan["pendencias_preparo"])
            self.summary.setText(
                f"{self.plan['protocolo']}\nVolume nominal: {r['quantidade_final']:g} mL; fator de escala: {r['fator_escala']:g}.\n{self.plan['formula_origem']}\n{self.plan['limites']}\n{pending}"
            )
        elif "resultado" in self.plan:
            r = self.plan["resultado"]
            references = "; ".join(
                f"{source['organization']}, {source['year']}, p. {', '.join(str(page) for page in source['paginas'])}"
                for source in self.plan["fontes"]
            )
            pending_label = (
                "\nDados opcionais de identificação/conservação não preenchidos no rótulo planejado."
                if self.plan.get("pendencias_rotulo")
                else ""
            )
            if self.plan.get("erros_rotulo"):
                pending_label += "\n" + " ".join(self.plan["erros_rotulo"].values())
            dose_label = (
                "Alíquota de estoque"
                if self.plan["tipo_calculo"] in {"diluicao", "seriada", "fator"}
                else "Reagente comercial"
            )
            detail = (
                f"\nFator de diluição: {r['fator_diluicao']:.6g}. {self.plan['observacao_diluicao']}"
                if self.plan["tipo_calculo"] in {"diluicao", "seriada", "fator"}
                else ""
            )
            self.summary.setText(
                f"{self.plan['protocolo']}\n{dose_label}: {r['quantidade_reagente']:.6g} {r['unidade_reagente']}\nSolvente/diluente: {self.plan['solvente']}{detail}\nFontes: {references}. {self.plan['limites']}{pending_label}"
            )
        else:
            if self.plan.get("erros_rotulo"):
                pending_label += "\n" + " ".join(self.plan["erros_rotulo"].values())
            self.summary.setText(
                f"{self.plan['protocolo']}\n{self.plan['n_amostras']} amostras · {self.plan['n_replicatas']} replicatas · {self.plan['n_controles']} controles · {self.plan['n_reacoes']} reações"
            )
        if self.plan.get("tipo_calculo") in {"volume", "recipientes"}:
            r = self.plan["resultado"]
            u = r["unidade_final"]
            self.summary.setText(
                f"{self.plan['protocolo']}\nVolume base: {r['volume_sem_excedente']:.6g} {u}\nExcedente: {r['volume_excedente']:.6g} {u}\nTotal a preparar: {r['quantidade_final']:.6g} {u}\n{self.plan['limites']}\nFontes: {references}."
            )
        if self.plan.get("tipo_calculo") == "recipientes":
            self.summary.setText(
                self.summary.text()
                + f"\n{self.plan['n_recipientes']} {self.plan['recipiente']}\n"
                + " ".join(self.plan["pendencias_preparo"])
            )
        if self.plan.get("tipo_calculo") == "desidratado":
            self.summary.setText(
                self.summary.text()
                + "\nInstrução declarada pelo pesquisador: "
                + self.plan["fonte_fabricante_declarada"]["referencia"]
                + "\n"
                + " ".join(self.plan["pendencias_preparo"])
            )
        from frontend.preparos import preencher_serie

        preencher_serie(self.serie_table, self.plan)
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

    def accept_percent_result(self, params, plan):
        if params == self.parameters and plan == self.plan:
            return
        if not self.flush_observations():
            self.invalidate_plan()
            self.show_pending_data()
            return
        if params != self.parameters and self.analysis is not None:
            self.analysis.set_experiment(self.title.text().strip(), plan)
        self.parameters, self.plan = params, plan
        self.percent_form.blockSignals(True)
        self.percent_form.set_values(params)
        self.percent_form.blockSignals(False)
        self.render_plan()
        self.export_button.setEnabled(True)
        self.continue_button.setEnabled(True)
        self.save_history()
        self.show_page(4)

    def build_plan(self):
        body = self.page(
            "Etapa 3 de 3",
            "Revise seu planejamento.",
            "Confira os dados calculados, o procedimento e suas fontes.",
        )
        self.result_title = label("", 20, True)
        body.addWidget(self.result_title)
        self.summary = label("")
        body.addWidget(self.summary)
        self.serie_table = QTableWidget()
        self.serie_table.hide()
        body.addWidget(self.serie_table)
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
                "Quantidades calculadas para o preparo informado. Verifique os materiais e as condições exigidos pelo experimento.",
                12,
            )
        )
        body.addWidget(label("Organização e procedimento", 16, True))
        self.procedure = label("")
        body.addWidget(self.procedure)
        self.export_button = button("Exportar planejamento em JSON", self.export_plan)
        self.export_button.setEnabled(False)
        body.addWidget(self.export_button)
        self.continue_button = button(
            "Ver resultados e ajustar parâmetros", lambda: self.show_page(4), True
        )
        self.continue_button.setToolTip(
            "Disponível após gerar um planejamento com cálculos implementados."
        )
        body.addWidget(self.continue_button)
        self.export_status = label("")
        body.addWidget(self.export_status)
        body.addWidget(button("Editar parâmetros", lambda: self.show_page(2)))
        body.addStretch()

    def export_plan(self):
        if self.plan is None:
            return
        path, _ = QFileDialog.getSaveFileName(
            self, "Exportar planejamento", "planejamento.json", "JSON (*.json)"
        )
        if not path:
            return
        try:
            self.write_export(Path(path))
        except OSError as exc:
            self.export_status.setText(f"Não foi possível salvar: {exc}")
            return
        self.export_status.setText(f"Planejamento exportado: {Path(path).name}")

    def export_payload(self):
        if self.plan is None:
            raise ValueError("Gere um plano válido antes de exportar.")
        payload = {
            "titulo": self.title.text().strip(),
            "fontes": self.plan.get("fontes", []),
            "protocolo_id": self.plan.get("protocolo_id", self.protocol.currentData()),
            "parametros": self.parameters,
            "plano": self.plan,
        }
        if self.analysis is not None:
            observed = self.analysis.observation_payload()
            if observed is not None:
                payload["resultados_observados"] = observed
        return payload

    def write_export(self, path):
        payload = self.export_payload()
        path.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2, allow_nan=False),
            encoding="utf-8",
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
    from frontend.plotting import configure_cache

    configure_cache()
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
    app.setFont(QFont("Segoe UI" if sys.platform == "win32" else "Helvetica Neue", 13))
    app.setStyleSheet("""
        QFrame#sidebar { background: palette(base); border-right: 1px solid palette(mid); }
        QGroupBox { background: palette(base); border: 1px solid palette(mid); border-radius: 8px; margin-top: 16px; padding: 24px; }
        QGroupBox[foldable="true"]:!checked { border: none; background: transparent; padding: 0px; }
        QGroupBox[foldable="true"]::indicator { width: 14px; height: 14px; border: 1px solid palette(mid); background: palette(base); }
        QGroupBox[foldable="true"]::indicator:checked { background: palette(highlight); }
        QGroupBox::title { subcontrol-origin: margin; left: 16px; }
        QPushButton { background: palette(button); padding: 8px 16px; border: 1px solid palette(mid); border-radius: 6px; }
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
