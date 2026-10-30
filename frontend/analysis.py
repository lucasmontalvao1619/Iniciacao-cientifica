"""Entrada de medições, estatística do service e gráfico dos dados observados."""

import csv
import io
import math
import textwrap
from pathlib import Path

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure
from PyQt6.QtWidgets import (
    QCheckBox,
    QDoubleSpinBox,
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

from planejador.core.exceptions import ErroPlanejamento
from planejador.services import analisar_grupos


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


class AnalysisWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.report = None
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
            "Uma linha por grupo. Digite os valores separados por ponto e vírgula: 1,2; 1,4; 1,3. Use somente medições observadas, não os valores planejados."
        )
        explanation.setWordWrap(True)
        layout.addWidget(explanation)
        self.data = QTableWidget(2, 2)
        self.data.setHorizontalHeaderLabels(
            ["Nome do grupo", "Valores medidos (separe com ;)"]
        )
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
        self.unit = QLineEdit()
        self.unit.setMaxLength(80)
        self.unit.setPlaceholderText("Ex.: absorbância, UFC/mL, mg/mL")
        unit_label = QLabel(
            "O que foi medido? Informe a unidade ou grandeza do gráfico"
        )
        unit_label.setBuddy(self.unit)
        layout.addWidget(unit_label)
        layout.addWidget(self.unit)
        run = QPushButton("Ver resumo e gráfico")
        run.setMinimumHeight(42)
        run.clicked.connect(self.analyze)
        layout.addWidget(run)
        advanced_toggle = QCheckBox(
            "Mostrar opções avançadas de comparação entre grupos"
        )
        layout.addWidget(advanced_toggle)
        self.advanced = QWidget()
        advanced_layout = QVBoxLayout(self.advanced)
        advanced_layout.setContentsMargins(0, 0, 0, 0)
        self.advanced.setVisible(False)
        advanced_toggle.toggled.connect(self.advanced.setVisible)
        self.infer = QCheckBox("Aplicar comparação estatística a grupos independentes")
        advanced_layout.addWidget(self.infer)
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
            "A comparação usa t de Student para dois grupos e ANOVA para três ou mais. Independência, normalidade e homogeneidade de variâncias devem ser avaliadas no desenho do estudo; não são verificadas automaticamente."
        )
        note.setWordWrap(True)
        advanced_layout.addWidget(note)
        layout.addWidget(self.advanced)
        self.status = QLabel("Aguardando medições.")
        self.status.setWordWrap(True)
        layout.addWidget(self.status)
        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(
            ["Grupo", "Medições", "Média", "Variação (desvio padrão)", "Variância"]
        )
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.ResizeToContents
        )
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setMinimumHeight(140)
        self.table.setMaximumHeight(150)
        layout.addWidget(self.table)
        self.figure = Figure(figsize=(6, 3), layout="constrained")
        self.canvas = FigureCanvasQTAgg(self.figure)
        self.canvas.setMinimumHeight(300)
        layout.addWidget(self.canvas, 1)
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

    def remove_group(self):
        row = self.data.currentRow()
        if row >= 0:
            self.data.removeRow(row)
            self.invalidate()

    def clear_experiment(self):
        self.context = None
        self.data.clearContents()
        self.data.setRowCount(2)
        self.unit.clear()
        self.infer.setChecked(False)
        self.alpha.setValue(0.05)
        self.context_label.setText("Conclua o planejamento para registrar as medições.")
        self.invalidate()

    def set_experiment(self, title, plan):
        self.clear_experiment()
        self.context = {
            "titulo": title,
            "protocolo": plan["protocolo"],
            "amostras": plan["n_amostras"],
            "replicatas": plan["n_replicatas"],
            "controles": plan["n_controles"],
        }
        self.context_label.setText(
            f"{title} · {plan['protocolo']}\nPlanejado · Amostras: {plan['n_amostras']} · Repetições por amostra: {plan['n_replicatas']} · Controles: {plan['n_controles']}. Os valores observados abaixo serão associados a este planejamento."
        )
        self.status.setText(
            "Preencha os grupos e valores obtidos na bancada. Nenhuma medição é preenchida automaticamente."
        )

    def read_groups(self):
        stream = io.StringIO()
        writer = csv.writer(stream, delimiter=";")
        names = set()
        for row in range(self.data.rowCount()):
            name = (
                self.data.item(row, 0).text().strip() if self.data.item(row, 0) else ""
            )
            values = (
                self.data.item(row, 1).text().strip() if self.data.item(row, 1) else ""
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
        self.report = None
        self.table.setRowCount(0)
        self.figure.clear()
        self.canvas.draw_idle()
        self.save.setEnabled(False)
        self.save_experiment.setEnabled(False)
        self.status.setText(
            "Clique em Ver resumo e gráfico após informar ou editar os valores."
        )

    def analyze(self):
        self.invalidate()
        try:
            if self.context is None:
                raise ValueError("Conclua o planejamento antes de analisar.")
            if not self.unit.text().strip():
                self.unit.setFocus()
                raise ValueError(
                    "Informe o que foi medido ou a unidade para identificar o gráfico."
                )
            groups = self.read_groups()
            if self.infer.isChecked():
                self.report = analisar_grupos(groups, alpha=self.alpha.value())
            else:
                self.report = {
                    "resumos": {
                        name: analisar_grupos({name: values})["resumos"][name]
                        for name, values in groups.items()
                    },
                    "teste_t": None,
                    "anova": None,
                }
        except (ValueError, ErroPlanejamento) as exc:
            self.status.setText(f"Não foi possível analisar: {exc}")
            return
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
        axes = self.figure.add_subplot()
        for i, values in enumerate(groups.values()):
            axes.scatter([i] * len(values), values, label=None)
        axes.set_xticks(
            range(len(groups)), [textwrap.fill(name, 20) for name in groups]
        )
        axes.set_ylabel(self.unit.text().strip(), wrap=True)
        axes.set_title(textwrap.fill(self.context["titulo"], 60), wrap=True)
        axes.set_xlabel("Grupo")
        axes.grid(axis="y", alpha=0.2)
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
