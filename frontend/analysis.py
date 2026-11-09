"""Entrada de medições, estatística do service e gráfico dos dados observados."""

import csv
import io
import json
import math
import textwrap
from pathlib import Path

from PyQt6.QtCore import QObject, QRunnable, Qt, QThreadPool, pyqtSignal
from PyQt6.QtGui import QKeySequence, QShortcut
from PyQt6.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
    QFileDialog,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QPushButton,
    QScrollArea,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from frontend.numeric import DecimalSpinBox as QDoubleSpinBox
from planejador.core.exceptions import ErroPlanejamento


def parse_measurements(text):
    groups = {}
    for number, row in enumerate(csv.reader(io.StringIO(text), delimiter=";"), 1):
        if not row or not any(cell.strip() for cell in row):
            continue
        if number == 1 and [c.strip().lower() for c in row] == ["grupo", "valor"]:
            continue
        if len(row) != 2 or not row[0].strip():
            raise ValueError(f"Linha {number}: informe grupo;valor.")
        try:
            value = float(row[1].strip().replace(",", "."))
        except ValueError as exc:
            raise ValueError(f"Linha {number}: valor numérico inválido.") from exc
        if not math.isfinite(value):
            raise ValueError(f"Linha {number}: use um valor finito.")
        groups.setdefault(row[0].strip(), []).append(value)
    if not groups:
        raise ValueError("Insira pelo menos uma medição.")
    return groups


def calculate_report(groups, infer, alpha):
    from planejador.services import analisar_grupos

    if infer:
        report = analisar_grupos(groups, alpha=alpha)
    else:
        report = {
            "resumos": {
                name: analisar_grupos({name: values})["resumos"][name]
                for name, values in groups.items()
            },
            "teste_t": None,
            "anova": None,
        }
    try:
        json.dumps(report, allow_nan=False)
    except ValueError as exc:
        raise ValueError(
            "Resultado estatístico indefinido ou fora da faixa numérica. Revise os dados e os pressupostos; pode desativar a comparação para consultar o resumo descritivo."
        ) from exc
    return report


class AnalysisSignals(QObject):
    finished = pyqtSignal(object)


class AnalysisJob(QRunnable):
    def __init__(self, groups, infer, alpha, revision):
        super().__init__()
        self.groups, self.infer, self.alpha, self.revision = (
            groups,
            infer,
            alpha,
            revision,
        )
        self.signals = AnalysisSignals()

    def run(self):
        try:
            result = calculate_report(self.groups, self.infer, self.alpha)
            from frontend.plotting import load_figure

            load_figure()
        except Exception as exc:
            result = str(exc)
        self.signals.finished.emit((self.revision, self.groups, result))


class MeasurementsTable(QTableWidget):
    """Uma linha por grupo; colagem retangular como em uma planilha."""

    def __init__(self):
        super().__init__(2, 4)
        self.update_headers()
        self.paste_shortcut = QShortcut(QKeySequence.StandardKey.Paste, self)
        self.paste_shortcut.setContext(Qt.ShortcutContext.WidgetWithChildrenShortcut)
        self.paste_shortcut.activated.connect(
            lambda: self.parentWidget().paste_measurements()
        )

    def update_headers(self):
        self.setHorizontalHeaderLabels(
            ["Grupo"] + [f"Medição {i}" for i in range(1, self.columnCount())]
        )

    def add_measurement(self):
        self.setColumnCount(self.columnCount() + 1)
        self.update_headers()

    def paste_cells(self):
        rows = list(
            csv.reader(io.StringIO(QApplication.clipboard().text()), delimiter="\t")
        )
        if not rows or not any(rows):
            return
        row, col = max(0, self.currentRow()), max(0, self.currentColumn())
        # Limite da entrada interativa; não alocar uma planilha inteira por engano.
        if len(rows) * max(map(len, rows), default=0) > 10000:
            raise ValueError("Cole até 10.000 células por vez.")
        self.blockSignals(True)
        try:
            self.setRowCount(max(self.rowCount(), row + len(rows)))
            self.setColumnCount(max(self.columnCount(), col + max(map(len, rows))))
            self.update_headers()
            for i, values in enumerate(rows):
                for j, value in enumerate(values):
                    self.setItem(row + i, col + j, QTableWidgetItem(value))
        finally:
            self.blockSignals(False)
        self.itemChanged.emit(self.item(row, col))


class AnalysisWidget(QWidget):
    changed = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.report = None
        self.revision = 0
        self.worker = None
        self.context = None
        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 24, 32, 24)
        title = QLabel("Registre as medições do seu experimento")
        font = title.font()
        font.setPointSize(24)
        font.setBold(True)
        title.setFont(font)
        title.setWordWrap(True)
        layout.addWidget(title)
        self.context_label = QLabel(
            "Conclua o planejamento para registrar as medições."
        )
        self.context_label.setWordWrap(True)
        layout.addWidget(self.context_label)
        explanation = QLabel(
            "Uma linha por grupo e uma medição por célula. Cole do Excel com a primeira coluna contendo os grupos e as seguintes contendo os números, sem cabeçalho. Use somente valores observados na bancada."
        )
        explanation.setWordWrap(True)
        layout.addWidget(explanation)
        self.data = MeasurementsTable()
        self.data.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )
        self.data.setAccessibleName("Grupos e valores medidos")
        self.data.setMinimumHeight(150)
        self.data.setMaximumHeight(170)
        layout.addWidget(self.data)
        controls = QHBoxLayout()
        add = QPushButton("Adicionar grupo")
        add.clicked.connect(lambda: self.data.insertRow(self.data.rowCount()))
        controls.addWidget(add)
        remove = QPushButton("Remover grupo selecionado")
        remove.clicked.connect(self.remove_group)
        controls.addWidget(remove)
        layout.addLayout(controls)
        paste_row = QHBoxLayout()
        paste = QPushButton("Colar do Excel")
        paste.clicked.connect(self.paste_measurements)
        paste_row.addWidget(paste)
        add_value = QPushButton("Adicionar medição")
        add_value.clicked.connect(self.data.add_measurement)
        paste_row.addWidget(add_value)
        layout.addLayout(paste_row)
        self.unit = QLineEdit()
        self.unit.setMaxLength(80)
        self.unit.setPlaceholderText("Ex.: absorbância, UFC/mL, mg/mL")
        unit_label = QLabel(
            "O que foi medido? Informe a unidade ou grandeza do gráfico"
        )
        unit_label.setWordWrap(True)
        unit_label.setBuddy(self.unit)
        layout.addWidget(unit_label)
        layout.addWidget(self.unit)
        self.run_button = QPushButton("Ver resumo e gráfico")
        self.run_button.setMinimumHeight(42)
        self.run_button.clicked.connect(self.start_analysis)
        layout.addWidget(self.run_button)
        advanced_toggle = QCheckBox("Comparar grupos (opções avançadas)")
        layout.addWidget(advanced_toggle)
        self.advanced = QWidget()
        advanced_layout = QVBoxLayout(self.advanced)
        advanced_layout.setContentsMargins(0, 0, 0, 0)
        self.advanced.setVisible(False)
        advanced_toggle.toggled.connect(self.advanced.setVisible)
        self.infer = QCheckBox("Aplicar comparação estatística a grupos independentes")
        advanced_layout.addWidget(self.infer)
        design_label = QLabel(
            "As medições vêm de unidades experimentais independentes?"
        )
        design_label.setWordWrap(True)
        advanced_layout.addWidget(design_label)
        self.design = QComboBox()
        self.design.addItems(
            [
                "Não sei / ainda não conferi",
                "Sim, são independentes",
                "Não, são pareadas ou medidas repetidas",
            ]
        )
        advanced_layout.addWidget(self.design)
        design_help = QLabel(
            "Repetir a leitura do mesmo tubo não cria uma nova unidade independente. Dados pareados precisam de outra análise, ainda indisponível aqui."
        )
        design_help.setWordWrap(True)
        advanced_layout.addWidget(design_help)
        self.assumptions = QCheckBox(
            "Os pressupostos do teste foram conferidos?"
        )
        advanced_layout.addWidget(self.assumptions)
        self.alpha = QDoubleSpinBox()
        self.alpha.setRange(0.001, 0.999)
        self.alpha.setDecimals(3)
        self.alpha.setValue(0.05)
        self.alpha.setFixedWidth(110)
        alpha_row = QHBoxLayout()
        alpha_label = QLabel("Nível de significância (padrão: 0,05)")
        alpha_label.setBuddy(self.alpha)
        alpha_row.addWidget(alpha_label)
        alpha_row.addWidget(self.alpha)
        advanced_layout.addLayout(alpha_row)
        note = QLabel(
            "A comparação usa t de Student para dois grupos e ANOVA para três ou mais. É preciso avaliar se a distribuição dos dados e a dispersão entre grupos atendem ao teste (normalidade e homogeneidade de variâncias). Se não tiver certeza, mantenha apenas o resumo. O aplicativo não verifica esses pressupostos automaticamente."
        )
        note.setWordWrap(True)
        advanced_layout.addWidget(note)
        layout.addWidget(self.advanced)
        self.status = QLabel("Aguardando medições.")
        self.status.setWordWrap(True)
        layout.addWidget(self.status)
        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(
            ["Grupo", "Medições", "Média", "Desvio padrão", "Variância"]
        )
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.ResizeToContents
        )
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setMinimumHeight(140)
        self.table.setMaximumHeight(150)
        layout.addWidget(self.table)
        self.figure = None
        self.canvas = None
        self.graph_layout = QVBoxLayout()
        layout.addLayout(self.graph_layout)
        self.save = QPushButton("Salvar gráfico em PNG")
        self.save.setEnabled(False)
        self.save.clicked.connect(self.save_graph)
        layout.addWidget(self.save)
        self.data.itemChanged.connect(self.invalidate)
        self.unit.textChanged.connect(self.invalidate)
        self.save_experiment = QPushButton("Salvar planejamento e resultados em JSON")
        self.save_experiment.setEnabled(False)
        layout.addWidget(self.save_experiment)
        self.back = QPushButton("Voltar ao plano deste experimento")
        layout.addWidget(self.back)
        self.infer.toggled.connect(self.invalidate)
        self.alpha.valueChanged.connect(self.invalidate)
        self.design.currentIndexChanged.connect(self.invalidate)
        self.assumptions.toggled.connect(self.invalidate)

    def paste_measurements(self):
        try:
            self.data.paste_cells()
        except ValueError as exc:
            self.status.setText(str(exc))

    def remove_group(self):
        row = self.data.currentRow()
        if row >= 0:
            self.data.removeRow(row)
            self.invalidate()

    def clear_experiment(self):
        self.context = None
        self.data.clearContents()
        self.data.setRowCount(2)
        self.data.setColumnCount(4)
        self.data.update_headers()
        self.design.setCurrentIndex(0)
        self.assumptions.setChecked(False)
        self.unit.clear()
        self.infer.setChecked(False)
        self.alpha.setValue(0.05)
        self.context_label.setText("Conclua o planejamento para registrar as medições.")
        self.invalidate()

    def set_experiment(self, title, plan):
        self.clear_experiment()
        self.context = {"titulo": title, "protocolo": plan["protocolo"]}
        if "protocolo_id" in plan:
            self.context["protocolo_id"] = plan["protocolo_id"]
        detail = ""
        if "n_amostras" in plan:
            self.context.update(
                amostras=plan["n_amostras"],
                replicatas=plan["n_replicatas"],
                controles=plan["n_controles"],
            )
            detail = f"Planejado · Amostras: {plan['n_amostras']} · Repetições por amostra: {plan['n_replicatas']} · Controles: {plan['n_controles']}. "
        heading = (
            title if title == plan["protocolo"] else f"{title} · {plan['protocolo']}"
        )
        self.context_label.setText(
            f"{heading}\n{detail}As medições abaixo pertencem a este planejamento. Alterar seus parâmetros limpa estas medições e a análise."
        )
        self.status.setText(
            "Preencha os grupos e valores obtidos na bancada. Nenhuma medição é preenchida automaticamente."
        )

    def observation_payload(self):
        if self.context is None:
            return None
        rows = [
            {
                "grupo": self.data.item(row, 0).text()
                if self.data.item(row, 0)
                else "",
                "valores": ";".join(
                    self.data.item(row, col).text()
                    for col in range(1, self.data.columnCount())
                    if self.data.item(row, col)
                    and self.data.item(row, col).text().strip()
                ),
            }
            for row in range(self.data.rowCount())
        ]
        rows = [row for row in rows if row["grupo"] or row["valores"]]
        if not rows and not self.unit.text().strip():
            return None
        payload = {
            "linhas_informadas": rows,
            "unidade": self.unit.text().strip(),
            "comparacao_solicitada": self.infer.isChecked(),
            "alpha": self.alpha.value(),
            "desenho_informado": self.design.currentText(),
            "pressupostos_conferidos": self.assumptions.isChecked(),
            "estado": "analisado" if self.report is not None else "rascunho",
        }
        if self.report is not None:
            payload.update(medicoes=self.read_groups(), analise=self.report)
        return payload

    def read_groups(self):
        stream = io.StringIO()
        writer = csv.writer(stream, delimiter=";")
        names = set()
        for row in range(self.data.rowCount()):
            name = (
                self.data.item(row, 0).text().strip() if self.data.item(row, 0) else ""
            )
            values = ";".join(
                self.data.item(row, col).text().strip()
                for col in range(1, self.data.columnCount())
                if self.data.item(row, col) and self.data.item(row, col).text().strip()
            )
            if not name and not values:
                continue
            if not name or not values:
                self.data.setCurrentCell(row, 0 if not name else 1)
                self.data.setFocus()
                raise ValueError(
                    f"Linha {row + 1}: preencha o nome do grupo e seus valores."
                )
            if name.casefold() in names:
                raise ValueError(
                    f"Grupo repetido: {name}. Reúna os valores na mesma linha."
                )
            names.add(name.casefold())
            for value in values.split(";"):
                writer.writerow([name, value])
        return parse_measurements(stream.getvalue())

    def invalidate(self, *_):
        self.revision += 1
        self.report = None
        self.table.setRowCount(0)
        if self.figure is not None and self.figure.axes:
            self.figure.clear()
            self.canvas.hide()
        self.save.setEnabled(False)
        self.save_experiment.setEnabled(False)
        self.status.setText(
            "Clique em Ver resumo e gráfico após informar ou editar os valores."
        )

        if self.context is not None:
            self.changed.emit()

    def analysis_input(self):
        if self.context is None:
            raise ValueError("Conclua o planejamento antes de analisar.")
        if not self.unit.text().strip():
            self.unit.setFocus()
            raise ValueError(
                "Informe o que foi medido ou a unidade para identificar o gráfico."
            )
        groups = self.read_groups()
        if self.infer.isChecked():
            if self.design.currentIndex() != 1:
                raise ValueError(
                    "Confirme unidades independentes para comparar. Para dados pareados ou dúvida, desative a comparação e consulte o resumo."
                )
            if not self.assumptions.isChecked():
                raise ValueError(
                    "Confira os pressupostos antes de comparar; enquanto isso, desative a comparação para ver o resumo e o gráfico."
                )
        return groups

    def start_analysis(self):
        self.invalidate()
        try:
            groups = self.analysis_input()
        except (ValueError, ErroPlanejamento) as exc:
            self.status.setText(f"Não foi possível analisar: {exc}")
            return
        self.run_button.setEnabled(False)
        self.status.setText(
            "Calculando resumo e gráfico… Você pode continuar usando a janela."
        )
        self.worker = AnalysisJob(
            groups, self.infer.isChecked(), self.alpha.value(), self.revision
        )
        self.worker.signals.finished.connect(self.finish_analysis)
        QThreadPool.globalInstance().start(self.worker)

    def finish_analysis(self, outcome):
        revision, groups, result = outcome
        self.worker = None
        self.run_button.setEnabled(True)
        if revision != self.revision:
            self.status.setText(
                "Os dados mudaram durante o cálculo. Clique em Ver resumo e gráfico para analisar os valores atuais."
            )
            return
        if isinstance(result, str):
            self.status.setText(f"Não foi possível analisar: {result}")
            return
        self.report = result
        self.render_analysis(groups)

    def analyze(self):
        self.invalidate()
        try:
            groups = self.analysis_input()
            self.report = calculate_report(
                groups, self.infer.isChecked(), self.alpha.value()
            )
        except (ValueError, ErroPlanejamento) as exc:
            self.report = None
            self.status.setText(f"Não foi possível analisar: {exc}")
            return
        self.render_analysis(groups)

    def render_analysis(self, groups):
        self.table.setRowCount(len(groups))
        for i, (name, summary) in enumerate(self.report["resumos"].items()):
            for j, value in enumerate(
                [
                    name,
                    summary["n"],
                    summary["media"],
                    summary["desvio_padrao"],
                    summary["variancia"],
                ]
            ):
                text = (
                    f"{value:.5g}"
                    if isinstance(value, float) and math.isfinite(value)
                    else str(value)
                )
                if isinstance(value, float) and not math.isfinite(value):
                    text = "não definido"
                self.table.setItem(i, j, QTableWidgetItem(text))
        if self.figure is None:
            from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg

            from frontend.plotting import load_figure

            self.figure = load_figure()(figsize=(6, 3.8), layout="constrained")
            self.canvas = FigureCanvasQTAgg(self.figure)
            self.canvas.setMinimumHeight(360)
            self.graph_layout.addWidget(self.canvas)
        self.figure.clear()
        axes = self.figure.add_subplot()
        for i, (name, values) in enumerate(groups.items()):
            offsets = [
                i - 0.18 + 0.12 * j / max(1, len(values) - 1)
                for j in range(len(values))
            ]
            axes.scatter(
                offsets, values, alpha=0.75, label="Medições" if i == 0 else None
            )
            summary = self.report["resumos"][name]
            axes.errorbar(
                i,
                summary["media"],
                yerr=summary["desvio_padrao"],
                fmt="D",
                color="black",
                capsize=5,
                label="Média ± desvio padrão" if i == 0 else None,
            )
        axes.legend(fontsize="small")
        axes.set_xticks(
            range(len(groups)), [textwrap.fill(name, 20) for name in groups]
        )
        axes.set_ylabel(self.unit.text().strip(), wrap=True)
        axes.set_title(textwrap.fill(self.context["titulo"], 60), wrap=True)
        axes.set_xlabel("Grupo")
        axes.grid(axis="y", alpha=0.2)
        self.canvas.show()
        self.canvas.draw_idle()
        test = self.report.get("teste_t") or self.report.get("anova")
        if test:
            kind = "t de Student" if self.report.get("teste_t") else "ANOVA de uma via"
            self.status.setText(
                f"{kind}: p = {test['valor_p']:.5g}; α = {self.alpha.value():.3g}. Interprete junto dos pressupostos e do desenho experimental."
            )
        else:
            self.status.setText(
                "Resumo calculado. A média mostra o valor central; o desvio padrão mostra a dispersão dos valores. Cada ponto do gráfico é uma medição. Nenhuma comparação estatística foi aplicada."
            )
        self.report["experimento"] = dict(self.context)
        self.report["unidade"] = self.unit.text().strip()
        self.save.setEnabled(True)
        self.save_experiment.setEnabled(True)
        self.changed.emit()
        parent = self.parentWidget()
        while parent is not None:
            if isinstance(parent, QScrollArea):
                parent.ensureWidgetVisible(self.table, 0, 24)
                break
            parent = parent.parentWidget()

    def save_graph(self):
        path, _ = QFileDialog.getSaveFileName(
            self, "Salvar gráfico", "grafico.png", "PNG (*.png)"
        )
        if path:
            try:
                self.figure.savefig(Path(path), dpi=160)
            except OSError as exc:
                self.status.setText(f"Falha ao salvar: {exc}")
