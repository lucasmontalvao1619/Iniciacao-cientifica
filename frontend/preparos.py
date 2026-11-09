"""Parâmetros específicos de preparos e resultados recalculados ao editar."""

from PyQt6.QtCore import QThreadPool, pyqtSignal
from PyQt6.QtWidgets import (
    QAbstractItemView,
    QCheckBox,
    QComboBox,
    QFormLayout,
    QGroupBox,
    QHeaderView,
    QLabel,
    QLineEdit,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from frontend.numeric import DecimalSpinBox as QDoubleSpinBox
from frontend.numeric import IntegerSpinBox as QSpinBox


def preencher_serie(table, plan):
    steps = plan.get("etapas", [])
    table.setVisible(bool(steps))
    table.setRowCount(len(steps))
    if not steps:
        return
    table.setColumnCount(6)
    table.setHorizontalHeaderLabels(
        [
            "Etapa",
            f"C ({plan['unidade_concentracao']})",
            "Fator total",
            "Alíquota\n(mL)",
            "Diluente nominal\n(mL)",
            "Restante\n(mL)",
        ]
    )
    table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
    table.verticalHeader().hide()
    table.horizontalHeader().setSectionResizeMode(
        QHeaderView.ResizeMode.ResizeToContents
    )
    table.setMinimumHeight(200)
    for row, step in enumerate(steps):
        for col, key in enumerate(
            (
                "etapa",
                "concentracao",
                "fator_acumulado",
                "volume_transferido_mL",
                "volume_diluente_nominal_mL",
                "volume_restante_mL",
            )
        ):
            table.setItem(row, col, QTableWidgetItem(f"{step[key]:.6g}"))


class PreparoForm(QWidget):
    changed = pyqtSignal()

    def __init__(self, tipo="percentual"):
        super().__init__()
        self.tipo = tipo
        self.formula_form = None
        self.comercial_form = None
        form = QFormLayout(self)
        form.setRowWrapPolicy(QFormLayout.RowWrapPolicy.WrapLongRows)
        self.form = form
        form.setVerticalSpacing(12)
        form.setHorizontalSpacing(24)
        self.unidade_estoque = QComboBox()
        for unit in ("mg/mL", "µg/mL", "g/L", "mol/L", "U/mL"):
            self.unidade_estoque.addItem(unit, unit)
        form.addRow(
            "Em qual unidade a concentração do estoque será expressa?",
            self.unidade_estoque,
        )
        self.unidade_estoque.currentIndexChanged.connect(self.update_units)
        self.unidade_diluicao = QComboBox()
        for unit in (
            "mg/mL",
            "µg/mL",
            "g/L",
            "mol/L",
            "mmol/L",
            "U/mL",
            "% m/v",
            "% v/v",
        ):
            self.unidade_diluicao.addItem(unit, unit)
        form.addRow(
            "Qual é a unidade comum das duas concentrações?", self.unidade_diluicao
        )
        self.unidade_diluicao.currentIndexChanged.connect(self.update_units)
        self.concentracao_inicial = QDoubleSpinBox()
        self.concentracao_inicial.setRange(0, 1000000000)
        self.concentracao_inicial.setDecimals(6)
        self.concentracao_inicial.setSpecialValueText("Informe o valor")
        self.concentracao_inicial.valueChanged.connect(self.changed)
        form.addRow(
            "Qual é a concentração da solução-estoque?", self.concentracao_inicial
        )
        self.fator = QDoubleSpinBox()
        self.fator.setRange(0, 1000000)
        self.fator.setDecimals(6)
        self.fator.setSpecialValueText("Informe o fator")
        self.fator.valueChanged.connect(self.changed)
        form.addRow("Qual é o fator entre diluições (maior que 1)?", self.fator)
        self.n_diluicoes = QSpinBox()
        self.n_diluicoes.setRange(0, 100)
        self.n_diluicoes.setSpecialValueText("Informe a quantidade")
        self.n_diluicoes.valueChanged.connect(self.changed)
        form.addRow("Quantas diluições, sem contar o estoque?", self.n_diluicoes)
        self.igualar_ultimo = QCheckBox("Sim, retirar uma alíquota final")
        self.igualar_ultimo.toggled.connect(self.changed)
        form.addRow(
            "Deseja igualar os volumes, retirando também do último recipiente?",
            self.igualar_ultimo,
        )
        self.volume_alicota = QDoubleSpinBox()
        self.volume_alicota.setRange(0, 1000000000)
        self.volume_alicota.setDecimals(6)
        self.volume_alicota.setSuffix(" mL")
        self.volume_alicota.setSpecialValueText("Informe o valor")
        self.volume_alicota.valueChanged.connect(self.changed)
        form.addRow(
            "Qual volume do estoque será transferido (mL)?", self.volume_alicota
        )
        self.recipiente = QComboBox()
        self.recipiente.addItem("Selecione o recipiente", None)
        self.recipiente.addItem("Placas", "placas")
        self.recipiente.addItem("Tubos", "tubos")
        self.recipiente.currentIndexChanged.connect(self.changed)
        form.addRow("O meio será distribuído em placas ou tubos?", self.recipiente)
        self.formato_recipiente = QLineEdit()
        self.formato_recipiente.setMaxLength(2000)
        self.formato_recipiente.textChanged.connect(self.changed)
        form.addRow(
            "Qual formato/capacidade do recipiente? (opcional)", self.formato_recipiente
        )
        self.metodo_distribuicao = QLineEdit()
        self.metodo_distribuicao.setMaxLength(2000)
        self.metodo_distribuicao.textChanged.connect(self.changed)
        form.addRow(
            "Qual método orienta volume, preparo e distribuição? (opcional)",
            self.metodo_distribuicao,
        )
        self.unidade_volume = QComboBox()
        for unit in ("µL", "mL", "L"):
            self.unidade_volume.addItem(unit, unit)
        self.unidade_volume.currentIndexChanged.connect(self.update_units)
        form.addRow("Qual é a unidade de volume?", self.unidade_volume)
        self.n_unidades = QSpinBox()
        self.n_unidades.setRange(0, 1000000)
        self.n_unidades.setSpecialValueText("Informe a quantidade")
        self.n_unidades.valueChanged.connect(self.changed)
        form.addRow(
            "Quantas unidades receberão o volume, incluindo controles e repetições?",
            self.n_unidades,
        )
        self.excesso_volume = QDoubleSpinBox()
        self.excesso_volume.setRange(0, 1000000)
        self.excesso_volume.setDecimals(6)
        self.excesso_volume.setSuffix(" %")
        self.excesso_volume.setSpecialValueText("Sem excedente (0%)")
        self.excesso_volume.valueChanged.connect(self.changed)
        form.addRow(
            "Qual percentual acrescentar ao volume base? (0 = nenhum)",
            self.excesso_volume,
        )
        self.base = QComboBox()
        for title, value in [
            ("Massa/volume (% m/v)", "m/v"),
            ("Volume/volume (% v/v)", "v/v"),
            ("Massa/massa (% m/m)", "m/m"),
        ]:
            self.base.addItem(title, value)
        form.addRow("Como a concentração percentual será expressa?", self.base)
        self.soluto, self.solvente = QLineEdit(), QLineEdit()
        self.soluto.setPlaceholderText("Reagente indicado no seu experimento")
        self.solvente.setPlaceholderText("Solvente indicado no seu experimento")
        for label, widget in [
            ("Qual é o soluto/reagente? (opcional)", self.soluto),
            ("Qual é o solvente de dissolução? (opcional)", self.solvente),
        ]:
            widget.setMaxLength(160)
            form.addRow(label, widget)
            widget.textChanged.connect(self.changed)
        self.diluente = QLineEdit()
        self.diluente.setMaxLength(160)
        self.diluente.setPlaceholderText("Vazio: usar o mesmo solvente informado")
        self.diluente.textChanged.connect(self.changed)
        form.addRow("Qual líquido completa o volume final? (opcional)", self.diluente)
        self.concentracao, self.quantidade_final, self.pureza = (
            QDoubleSpinBox() for _ in range(3)
        )
        for widget, value, maximum in [
            (self.concentracao, 0, 1000000),
            (self.quantidade_final, 0, 1000000000),
            (self.pureza, 0, 100),
        ]:
            widget.setDecimals(6)
            widget.setRange(0, maximum)
            widget.setValue(value)
            widget.setSpecialValueText("Informe o valor")
            widget.valueChanged.connect(self.changed)
        self.concentracao.setSuffix(" %")
        form.addRow("Qual é a concentração desejada?", self.concentracao)
        form.addRow("Qual é a quantidade final da solução?", self.quantidade_final)
        self.correcao = QComboBox()
        self.correcao.addItem("Teor / pureza química (% m/m)", "pureza")
        self.correcao.addItem("Potência certificada (µg/mg)", "potencia")
        self.correcao.addItem("Atividade certificada (U/mg)", "atividade")
        form.addRow(
            "Qual informação do reagente será usada na correção?", self.correcao
        )
        self.correcao.currentIndexChanged.connect(self.update_units)
        self.pureza_label = QLabel()
        self.pureza_label.setWordWrap(True)
        form.addRow(self.pureza_label, self.pureza)
        self.pureza.setSuffix(" %")
        self.potencia = QDoubleSpinBox()
        self.potencia.setDecimals(6)
        self.potencia.setRange(0, 1000000000)
        self.potencia.setSpecialValueText("Informe o valor")
        self.potencia.valueChanged.connect(self.changed)
        self.potencia_label = QLabel()
        self.potencia_label.setWordWrap(True)
        form.addRow(self.potencia_label, self.potencia)
        self.equivalencia = QDoubleSpinBox()
        self.equivalencia.setDecimals(6)
        self.equivalencia.setRange(0, 1000000000)
        self.equivalencia.setSuffix(" U/µg")
        self.equivalencia.setSpecialValueText("Informe o valor")
        self.equivalencia.valueChanged.connect(self.changed)
        form.addRow(
            "Qual é a equivalência específica do certificado (U/µg)?", self.equivalencia
        )
        self.massa_molar, self.densidade = QDoubleSpinBox(), QDoubleSpinBox()
        for widget, unit, maximum, placeholder in [
            (self.massa_molar, " g/mol", 10000000, "Informe a massa molar"),
            (self.densidade, " g/mL", 1000, "Informe a densidade"),
        ]:
            widget.setDecimals(6)
            widget.setRange(0, maximum)
            widget.setSuffix(unit)
            widget.setSpecialValueText(placeholder)
            widget.valueChanged.connect(self.changed)
        self.forma = QComboBox()
        self.forma.addItem("Reagente pesado", "pesagem")
        self.forma.addItem("Líquido medido por volume", "volume")
        form.addRow(
            "Qual é a massa molar da forma química usada (g/mol)?", self.massa_molar
        )
        form.addRow("Como o reagente será medido?", self.forma)
        form.addRow("Qual é a densidade do reagente comercial (g/mL)?", self.densidade)
        self.forma.currentIndexChanged.connect(self.update_units)
        self.metadata_group = QGroupBox(
            "Identificação e conservação do estoque (opcional)"
        )
        self.metadata_group.setCheckable(True)
        self.metadata_group.setChecked(False)
        metadata_layout = QVBoxLayout(self.metadata_group)
        self.metadata_widget = QWidget()
        metadata_form = QFormLayout(self.metadata_widget)
        metadata_form.setRowWrapPolicy(QFormLayout.RowWrapPolicy.WrapLongRows)
        self.meta_fields = {}
        for key, question in [
            ("identificacao_estoque", "Qual será a identificação do estoque?"),
            ("responsavel", "Quem será responsável pelo preparo?"),
            ("lote_reagente", "Qual é o lote do reagente usado?"),
            ("data_preparo", "Qual é a data prevista de preparo (AAAA-MM-DD)?"),
            ("data_validade", "Qual validade foi definida pelo método (AAAA-MM-DD)?"),
            ("armazenamento", "Quais condições de conservação foram definidas?"),
            (
                "fonte_estabilidade",
                "Qual fonte ou método fundamenta conservação e validade?",
            ),
        ]:
            field = QLineEdit()
            field.setMaxLength(300)
            field.textChanged.connect(self.changed)
            self.meta_fields[key] = field
            metadata_form.addRow(question, field)
            metadata_form.labelForField(field).setWordWrap(True)
            metadata_form.labelForField(field).setFixedWidth(230)
        metadata_layout.addWidget(self.metadata_widget)
        self.metadata_widget.hide()
        self.metadata_group.toggled.connect(self.metadata_widget.setVisible)
        form.addRow(self.metadata_group)
        self.note = QLabel(
            "Informe o teor do rótulo na base indicada. Volume é o volume FINAL da solução; o solvente é q.s.p. A compatibilidade e a solubilidade devem ser verificadas para o experimento."
        )
        self.note.setWordWrap(True)
        form.addRow(self.note)
        self.base.currentIndexChanged.connect(self.update_units)
        self.update_units()

    def set_protocol_type(self, tipo):
        if self.tipo != tipo:
            self.tipo = tipo
            if tipo == "recipientes":
                self.unidade_volume.setCurrentIndex(self.unidade_volume.findData("mL"))
            self.update_units()

    def update_units(self, *_):
        if not hasattr(self, "note"):
            return
        if self.tipo in {"formula", "desidratado"}:
            if self.tipo == "formula":
                if self.formula_form is None:
                    from frontend.formulacao import FormulaForm

                    self.formula_form = FormulaForm()
                    self.form.addRow(self.formula_form)
                    self.formula_form.changed.connect(self.changed.emit)
                selected_form = self.formula_form
            else:
                if self.comercial_form is None:
                    from frontend.meio_comercial import MeioComercialForm

                    self.comercial_form = MeioComercialForm()
                    self.form.addRow(self.comercial_form)
                    self.comercial_form.changed.connect(self.changed.emit)
                selected_form = self.comercial_form
            for row in range(self.form.rowCount()):
                self.form.setRowVisible(row, False)
            self.form.setRowVisible(selected_form, True)
            self.changed.emit()
            return
        if self.formula_form is not None or self.comercial_form is not None:
            for row in range(self.form.rowCount()):
                self.form.setRowVisible(row, True)
            for panel in (self.formula_form, self.comercial_form):
                if panel is not None:
                    self.form.setRowVisible(panel, False)
        containers = self.tipo == "recipientes"
        volume = self.tipo in {"volume", "recipientes"}
        for field in (
            self.recipiente,
            self.formato_recipiente,
            self.metodo_distribuicao,
        ):
            self.form.setRowVisible(field, containers)
        stock = self.tipo == "estoque"
        serial = self.tipo == "seriada"
        inverso = self.tipo == "fator"
        dilution = self.tipo in {"diluicao", "seriada", "fator"}
        unit = self.unidade_estoque.currentData()
        molar = self.tipo == "molar" or (stock and unit == "mol/L")
        unit_activity = stock and unit == "U/mL"
        activity = (
            stock
            and not molar
            and (unit_activity or self.correcao.currentData() == "atividade")
        )
        potent = (
            stock
            and not molar
            and (activity or self.correcao.currentData() in {"potencia", "atividade"})
        )
        base = self.base.currentData()
        q_unit = (
            self.unidade_volume.currentText()
            if volume
            else "g"
            if not stock and not molar and not dilution and base == "m/m"
            else "mL"
        )
        c_unit = (
            self.unidade_diluicao.currentData()
            if dilution
            else unit
            if stock
            else "mol/L"
            if molar
            else f"% {base}"
        )
        self.concentracao_inicial.setSuffix(f" {c_unit}")
        self.form.labelForField(self.concentracao_inicial).setText(
            f"Qual é a concentração da solução-estoque ({c_unit})?"
        )
        self.form.labelForField(self.soluto).setText(
            "Qual é a solução-estoque? (opcional)"
            if dilution
            else "Qual é o soluto/reagente? (opcional)"
        )
        self.form.labelForField(self.solvente).setText(
            "Qual é o diluente? (opcional)"
            if dilution
            else "Qual é o solvente de dissolução? (opcional)"
        )
        self.quantidade_final.setSuffix(f" {q_unit}")
        self.concentracao.setSuffix(f" {c_unit}")
        self.form.labelForField(self.concentracao).setText(
            f"Qual é a concentração desejada ({c_unit})?"
        )
        self.form.labelForField(self.quantidade_final).setText(
            f"Qual é a quantidade final da solução ({q_unit})?"
        )
        self.pureza_label.setText(
            "Qual é o teor do reagente (% v/v)?"
            if not stock and not molar and base == "v/v"
            else "Qual é a pureza do reagente (% m/m)?"
        )
        self.potencia_label.setText(
            "Qual é a atividade certificada (U/mg)?"
            if activity
            else "Qual é a potência certificada (µg/mg)?"
        )
        self.potencia.setSuffix(" U/mg" if activity else " µg/mg")
        self.form.setRowVisible(self.unidade_volume, volume)
        self.form.setRowVisible(self.n_unidades, volume)
        self.form.setRowVisible(self.excesso_volume, volume)
        self.form.setRowVisible(self.solvente, not volume)
        if volume:
            self.form.labelForField(self.soluto).setText(
                "Qual material será distribuído? (opcional)"
            )
            self.form.labelForField(self.quantidade_final).setText(
                f"Qual volume cada unidade receberá ({q_unit})?"
            )
        self.form.setRowVisible(self.fator, serial)
        self.form.setRowVisible(self.n_diluicoes, serial)
        self.form.setRowVisible(self.igualar_ultimo, serial)
        self.form.setRowVisible(
            self.concentracao, not serial and not inverso and not volume
        )
        self.form.setRowVisible(self.volume_alicota, inverso)
        if serial:
            self.form.labelForField(self.unidade_diluicao).setText(
                "Qual é a unidade de concentração da série?"
            )
            self.form.labelForField(self.quantidade_final).setText(
                "Qual volume preparar por etapa, antes de transferir ao próximo (mL)?"
            )
        else:
            self.form.labelForField(self.unidade_diluicao).setText(
                "Qual é a unidade da concentração do estoque?"
                if inverso
                else "Qual é a unidade comum das duas concentrações?"
            )
        self.form.setRowVisible(self.unidade_estoque, stock)
        self.form.setRowVisible(self.unidade_diluicao, dilution)
        self.form.setRowVisible(self.concentracao_inicial, dilution)
        self.form.setRowVisible(
            self.base, not stock and not molar and not dilution and not volume
        )
        self.form.setRowVisible(
            self.correcao, stock and not molar and not unit_activity
        )
        self.form.setRowVisible(self.pureza, not potent and not dilution and not volume)
        self.form.setRowVisible(self.potencia, potent)
        self.form.setRowVisible(self.equivalencia, activity and not unit_activity)
        self.form.setRowVisible(self.massa_molar, molar)
        self.form.setRowVisible(self.forma, molar or stock)
        self.form.setRowVisible(
            self.densidade, (molar or stock) and self.forma.currentData() == "volume"
        )
        self.form.setRowVisible(self.diluente, stock)
        self.form.setRowVisible(self.metadata_group, stock)
        if volume:
            self.note.setText(
                "Informe o volume por unidade e o total de unidades que receberão esse volume. Inclua controles e repetições na contagem, sem multiplicá-los novamente. O percentual é um acréscimo sobre o volume base; 0 significa nenhuma reserva. A composição e a margem apropriada dependem do método. A reserva não aumenta a dose de cada unidade. Os números não são convertidos ao mudar a unidade."
            )
        elif inverso:
            self.note.setText(
                "Informe a concentração do estoque, a alíquota transferida e o volume FINAL preparado, sem somar volumes presumidamente aditivos. O programa calcula fator = volume final/alíquota e concentração final = concentração inicial/fator. A alíquota não pode superar o volume final. Identificações são opcionais; não use % m/m nesta fórmula volumétrica."
            )
        elif serial:
            self.note.setText(
                "A etapa 1 já é a primeira diluição do estoque. Homogeneizar antes de cada transferência. O volume informado é o preparado ANTES de retirar a alíquota para o próximo recipiente; intermediários ficam com menos volume. O último só perde uma alíquota se você marcar a opção de igualar. Volumes são nominais: conferir compatibilidade e técnica do método."
            )
        elif dilution:
            self.note.setText(
                "Informe ambas as concentrações na mesma unidade por volume. A concentração desejada não pode superar a do estoque. O diluente completa q.s.p. ao volume FINAL; a diferença entre os volumes é somente nominal. Não use % m/m nesta fórmula volumétrica."
            )
        elif stock:
            self.note.setText(
                "Responda às perguntas usadas no cálculo. Potência e pureza são informações distintas. U/mL requer atividade em U/mg; a conversão entre U e µg só ocorre quando você informa a equivalência específica do certificado. Os dados de identificação/conservação são opcionais no planejamento e os ausentes ficam pendentes. Não há prazo universal de validade."
            )
        elif molar:
            self.note.setText(
                "Massa molar e teor devem corresponder à forma química do rótulo, incluindo hidratação quando houver. Para líquido medido por volume, informe a densidade do reagente comercial. O solvente é q.s.p. ao volume FINAL; não há conversão automática de teor % v/v para % m/m."
            )
        else:
            self.note.setText(
                "Informe o teor do rótulo na base indicada. Volume é o volume FINAL da solução; o solvente é q.s.p. A compatibilidade e a solubilidade devem ser verificadas para o experimento."
            )
        if containers:
            self.form.labelForField(self.soluto).setText(
                "Qual meio será distribuído? (opcional)"
            )
            self.form.labelForField(self.n_unidades).setText(
                "Quantas placas ou tubos, incluindo controles e repetições?"
            )
            self.form.labelForField(self.quantidade_final).setText(
                f"Qual volume cada placa ou tubo receberá ({q_unit})?"
            )
            # shortcut: uma dose por planejamento; usar grupos se houver demanda por lotes mistos.
            self.note.setText(
                "Planeje um tipo de recipiente e um volume por vez. Inclua controles e repetições na contagem. Formato e método ausentes ficam pendentes. O volume por recipiente é definido pelo método, não pela capacidade nominal; não há dose, ciclo ou validade universais. O excedente é acréscimo sobre a base, inclusive 0%; não aumenta a dose por recipiente. Os números não são convertidos ao mudar a unidade."
            )
        else:
            self.form.labelForField(self.n_unidades).setText(
                "Quantas unidades receberão o volume, incluindo controles e repetições?"
            )
        for row in range(self.form.rowCount()):
            item = self.form.itemAt(row, QFormLayout.ItemRole.LabelRole)
            if item and isinstance(item.widget(), QLabel):
                item.widget().setWordWrap(True)
                item.widget().setFixedWidth(230)
        self.fit_note()
        self.changed.emit()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.fit_note()

    def fit_note(self):
        # QFormLayout can underallocate wrapped spanning labels after a resize.
        margins = self.form.contentsMargins()
        width = max(1, self.width() - margins.left() - margins.right())
        self.note.setMinimumHeight(self.note.heightForWidth(width))

    def values(self):
        if self.tipo == "desidratado":
            return self.comercial_form.values()
        if self.tipo == "formula":
            return self.formula_form.values()
        params = {
            "soluto": self.soluto.text().strip(),
            "solvente": self.solvente.text().strip(),
            "concentracao": self.concentracao.value(),
            "quantidade_final": self.quantidade_final.value(),
        }
        if self.tipo in {"volume", "recipientes"}:
            return {
                **(
                    {
                        "recipiente": self.recipiente.currentData(),
                        "formato_recipiente": self.formato_recipiente.text().strip(),
                        "metodo_distribuicao": self.metodo_distribuicao.text().strip(),
                    }
                    if self.tipo == "recipientes"
                    else {}
                ),
                "soluto": self.soluto.text().strip(),
                "volume_unitario": self.quantidade_final.value(),
                "unidade_volume": self.unidade_volume.currentText(),
                "n_unidades": self.n_unidades.value(),
                "excesso_percentual": self.excesso_volume.value(),
            }
        if self.tipo == "seriada":
            params.pop("concentracao")
            params.update(
                concentracao_inicial=self.concentracao_inicial.value(),
                unidade_concentracao=self.unidade_diluicao.currentData(),
                fator=self.fator.value(),
                n_diluicoes=self.n_diluicoes.value(),
                igualar_ultimo=self.igualar_ultimo.isChecked(),
            )
            return params
        if self.tipo == "fator":
            params.pop("concentracao")
            params.update(
                concentracao_inicial=self.concentracao_inicial.value(),
                unidade_concentracao=self.unidade_diluicao.currentData(),
                volume_alicota=self.volume_alicota.value(),
            )
            return params
        if self.tipo == "diluicao":
            params.update(
                concentracao_inicial=self.concentracao_inicial.value(),
                unidade_concentracao=self.unidade_diluicao.currentData(),
            )
            return params
        stock = self.tipo == "estoque"
        unit = self.unidade_estoque.currentData()
        molar = self.tipo == "molar" or (stock and unit == "mol/L")
        if stock:
            correction = (
                "atividade"
                if unit == "U/mL"
                else "pureza"
                if molar
                else self.correcao.currentData()
            )
            params.update(
                unidade_concentracao=unit,
                correcao=correction,
                diluente=self.diluente.text().strip(),
            )
            params.update(
                {key: field.text().strip() for key, field in self.meta_fields.items()}
            )
            if correction in {"potencia", "atividade"}:
                params["potencia"] = self.potencia.value()
                if correction == "atividade" and unit != "U/mL":
                    params["equivalencia"] = self.equivalencia.value()
            else:
                params["pureza"] = self.pureza.value()
        else:
            params["pureza"] = self.pureza.value()
        if molar:
            params["massa_molar"] = self.massa_molar.value()
        if molar or stock:
            params["forma"] = self.forma.currentData()
            if self.forma.currentData() == "volume":
                params["densidade"] = self.densidade.value()
        else:
            params["base"] = self.base.currentData()
        return params

    def set_values(self, values):
        if self.tipo == "desidratado":
            self.comercial_form.set_values(values)
            return
        if self.tipo == "formula":
            self.formula_form.set_values(values)
            return
        for key, widget in [
            ("base", self.base),
            ("soluto", self.soluto),
            ("solvente", self.solvente),
            ("concentracao", self.concentracao),
            ("quantidade_final", self.quantidade_final),
            ("pureza", self.pureza),
            ("massa_molar", self.massa_molar),
            ("densidade", self.densidade),
            ("forma", self.forma),
            ("unidade_concentracao", self.unidade_estoque),
            ("correcao", self.correcao),
            ("potencia", self.potencia),
            ("equivalencia", self.equivalencia),
            ("fator", self.fator),
            ("volume_alicota", self.volume_alicota),
            ("recipiente", self.recipiente),
            ("formato_recipiente", self.formato_recipiente),
            ("metodo_distribuicao", self.metodo_distribuicao),
            ("unidade_volume", self.unidade_volume),
            ("n_unidades", self.n_unidades),
            ("excesso_percentual", self.excesso_volume),
            ("n_diluicoes", self.n_diluicoes),
            ("igualar_ultimo", self.igualar_ultimo),
            ("concentracao_inicial", self.concentracao_inicial),
            ("unidade_concentracao", self.unidade_diluicao),
            ("diluente", self.diluente),
            *self.meta_fields.items(),
        ]:
            widget.blockSignals(True)
            if isinstance(widget, QComboBox):
                defaults = {
                    "base": "m/v",
                    "forma": "pesagem",
                    "unidade_concentracao": "mg/mL",
                    "unidade_volume": "mL" if self.tipo == "recipientes" else "µL",
                    "recipiente": None,
                    "correcao": "pureza",
                }
                value = values.get(key, defaults[key])
                widget.setCurrentIndex(widget.findData(value))
            elif isinstance(widget, QCheckBox):
                widget.setChecked(values.get(key, False))
            elif isinstance(widget, QLineEdit):
                widget.setText(values.get(key, ""))
            else:
                widget.setValue(
                    values.get("volume_unitario", 0)
                    if self.tipo in {"volume", "recipientes"}
                    and key == "quantidade_final"
                    else values.get(key, 0)
                )
            widget.blockSignals(False)
        self.update_units()


class PreparoResults(QWidget):
    updated = pyqtSignal(dict, dict)
    invalid = pyqtSignal()

    def __init__(self, protocol, values):
        super().__init__()
        self.protocol = protocol
        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 24, 32, 24)
        title = QLabel(
            {
                "molar": "Resultados do preparo molar",
                "estoque": "Resultados da solução-estoque",
                "diluicao": "Resultados da diluição de solução-estoque",
                "seriada": "Resultados da diluição seriada",
                "fator": "Fator de diluição e concentração final",
                "volume": "Volume total e excedente",
                "recipientes": "Meio necessário para placas ou tubos",
                "formula": "Resultado da formulação",
                "desidratado": "Preparo de meio comercial desidratado",
            }.get(protocol["tipo_calculo"], "Resultados do preparo percentual")
        )
        title.setWordWrap(True)
        layout.addWidget(title)
        instruction = QLabel(
            "Confira as quantidades calculadas. Para alterar os valores, abra Ajustar planejamento."
        )
        instruction.setWordWrap(True)
        layout.addWidget(instruction)
        self.form = PreparoForm(protocol["tipo_calculo"])
        self.form.set_values(values)
        self.adjustments = QGroupBox("Ajustar planejamento")
        self.adjustments.setCheckable(True)
        self.adjustments.setChecked(False)
        self.adjustments.setMaximumHeight(self.adjustments.fontMetrics().height() + 20)
        self.adjustments.toggled.connect(
            lambda on: self.adjustments.setMaximumHeight(
                16777215 if on else self.adjustments.fontMetrics().height() + 20
            )
        )
        QVBoxLayout(self.adjustments).addWidget(self.form)
        self.form.hide()
        self.adjustments.toggled.connect(self.form.setVisible)
        self.summary = QLabel()
        self.summary.setWordWrap(True)
        font = self.summary.font()
        font.setPointSize(16)
        font.setBold(True)
        self.summary.setFont(font)
        layout.addWidget(self.summary)
        layout.addWidget(self.adjustments)
        self.serie_table = QTableWidget()
        self.serie_table.hide()
        layout.addWidget(self.serie_table)
        self.component_plot = QComboBox()
        self.component_plot.setAccessibleName("Qual componente visualizar no gráfico?")
        self.component_plot.setSizeAdjustPolicy(
            QComboBox.SizeAdjustPolicy.AdjustToMinimumContentsLengthWithIcon
        )
        self.component_plot.setMinimumContentsLength(15)
        self.component_plot.setVisible(protocol["tipo_calculo"] == "formula")
        self.component_plot.currentIndexChanged.connect(self.recalculate)
        self.chart_group = QGroupBox("Simular quantidades no gráfico")
        self.chart_group.setCheckable(True)
        self.chart_group.setChecked(False)
        self.chart_group.setMaximumHeight(self.chart_group.fontMetrics().height() + 20)
        self.chart_body = QWidget()
        self.chart_layout = QVBoxLayout(self.chart_body)
        self.chart_layout.addWidget(self.component_plot)
        QVBoxLayout(self.chart_group).addWidget(self.chart_body)
        layout.addWidget(self.chart_group)
        self.chart_body.hide()
        self.figure = None
        self.font_job = None
        self.chart_status = QLabel()
        self.chart_status.setWordWrap(True)
        self.chart_layout.addWidget(self.chart_status)
        self.canvas = None
        self.chart_group.toggled.connect(self.toggle_chart)
        note = QLabel(
            "Gráfico de dimensionamento planejado; não representa medições, validação em bancada nem uma análise estatística de dados observados."
        )
        note.setWordWrap(True)
        self.chart_layout.addWidget(note)
        self.back = QPushButton("Voltar ao plano")
        layout.addWidget(self.back)
        self.save = QPushButton("Exportar planejamento e resultados em JSON")
        layout.addWidget(self.save)
        layout.addStretch()
        self.form.changed.connect(self.recalculate)
        self.recalculate()

    def toggle_chart(self, checked):
        self.chart_group.setMaximumHeight(
            16777215 if checked else self.chart_group.fontMetrics().height() + 20
        )
        self.chart_body.setVisible(checked)
        if checked:
            self.recalculate()

    def fonts_loaded(self, error):
        self.font_job = None
        self.chart_status.setText(f"Não foi possível abrir o gráfico: {error}" if error else "")
        if not error and self.chart_group.isChecked():
            self.recalculate()

    def prepare_chart(self, params, plan):
        if not self.chart_group.isChecked():
            self.updated.emit(params, plan)
            return False
        from frontend import plotting

        if not plotting.figure_ready:
            if self.font_job is None:
                self.chart_status.setText("Preparando fontes do gráfico… A janela continua disponível.")
                self.font_job = plotting.FontJob()
                self.font_job.signals.finished.connect(self.fonts_loaded)
                QThreadPool.globalInstance().start(self.font_job)
            self.updated.emit(params, plan)
            return False
        if self.figure is None:
            from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg

            self.figure = plotting.load_figure()(figsize=(6, 3.6), layout="constrained")
            self.canvas = FigureCanvasQTAgg(self.figure)
            self.canvas.setMinimumHeight(340)
            self.chart_layout.insertWidget(1, self.canvas)
        return True

    def recalculate(self):
        from planejador.core.exceptions import ErroPlanejamento
        from planejador.services.preparos import calcular_preparo

        params = self.form.values()
        if self.figure is not None:
            self.figure.clear()
        try:
            plan = calcular_preparo(self.protocol, params)
        except ErroPlanejamento as exc:
            self.summary.setText(str(exc))
            self.save.setEnabled(False)
            self.serie_table.setRowCount(0)
            self.serie_table.hide()
            self.invalid.emit()
            if self.canvas is not None:
                self.canvas.draw_idle()
            return
        self.save.setEnabled(True)
        if self.protocol["tipo_calculo"] == "formula":
            r = plan["resultado"]
            ingredients = plan["reagentes"]
            self.serie_table.setVisible(True)
            self.serie_table.setColumnCount(3)
            self.serie_table.setRowCount(len(ingredients))
            self.serie_table.setHorizontalHeaderLabels(
                ["Componente", "Quantidade planejada", "Unidade"]
            )
            self.serie_table.setEditTriggers(
                QAbstractItemView.EditTrigger.NoEditTriggers
            )
            self.serie_table.horizontalHeader().setSectionResizeMode(
                QHeaderView.ResizeMode.ResizeToContents
            )
            for row, item in enumerate(ingredients):
                for col, value in enumerate(
                    (item["nome"], f"{item['quantidade_total']:.6g}", item["unidade"])
                ):
                    self.serie_table.setItem(row, col, QTableWidgetItem(value))
            self.component_plot.blockSignals(True)
            previous = self.component_plot.currentData()
            self.component_plot.clear()
            for i, ingredient in enumerate(ingredients):
                self.component_plot.addItem(
                    f"{ingredient['nome']} ({ingredient['unidade']})", i
                )
            self.component_plot.setCurrentIndex(
                previous
                if isinstance(previous, int) and previous < len(ingredients)
                else 0
            )
            self.component_plot.blockSignals(False)
            ingredient = ingredients[self.component_plot.currentData()]
            self.component_plot.setToolTip(ingredient["nome"])
            pending = (
                "\n" + " ".join(plan["pendencias_preparo"])
                if plan["pendencias_preparo"]
                else ""
            )
            self.summary.setText(
                f"Volume nominal: {r['quantidade_final']:g} mL; fator de escala: {r['fator_escala']:g}.\n{plan['formula_origem']}{pending}"
            )
            if not self.prepare_chart(params, plan):
                return
            ax = self.figure.add_subplot(111)
            target = r["quantidade_final"]
            x = [target * i / 20 for i in range(21)]
            y = [ingredient["quantidade_total"] * (v / target) for v in x]
            ax.plot(x, y, color="#315e5b")
            ax.scatter([target], [ingredient["quantidade_total"]], color="#315e5b")
            ax.set_xlabel("Volume nominal da formulação (mL)")
            ax.set_ylabel(f"Quantidade ({ingredient['unidade']})")
            ax.set_title("Componente selecionado: quantidade proporcional ao volume")
            self.canvas.draw_idle()
            self.updated.emit(params, plan)
            return
        if self.protocol["tipo_calculo"] == "desidratado":
            r = plan["resultado"]
            pending = " ".join(plan["pendencias_preparo"])
            self.summary.setText(
                f"Meio desidratado: {r['quantidade_reagente']:.6g} g.\n{plan['solvente']}\nInstrução declarada: {plan['fonte_fabricante_declarada']['referencia']}\n{pending}"
            )
            if not self.prepare_chart(params, plan):
                return
            ax = self.figure.add_subplot(111)
            target = r["quantidade_final"]
            x = [target * i / 20 for i in range(21)]
            y = [r["quantidade_reagente"] * (v / target) for v in x]
            ax.plot(x, y, color="#315e5b")
            ax.scatter([target], [r["quantidade_reagente"]], color="#315e5b")
            ax.set_xlabel(
                "Volume de água (mL)"
                if plan["tipo_volume"] == "agua"
                else "Volume final (mL)"
            )
            ax.set_ylabel("Massa de meio desidratado (g)")
            ax.set_title("Proporção informada pelo pesquisador, conforme instrução")
            self.canvas.draw_idle()
            self.updated.emit(params, plan)
            return
        if self.protocol["tipo_calculo"] in {"volume", "recipientes"}:
            r = plan["resultado"]
            unit = params["unidade_volume"]
            n = params["n_unidades"]
            v = params["volume_unitario"]
            e = params["excesso_percentual"]
            self.summary.setText(
                f"Volume base: {r['volume_sem_excedente']:.6g} {unit}\nExcedente: {r['volume_excedente']:.6g} {unit} ({e:g}%)\nVolume total a preparar: {r['quantidade_final']:.6g} {unit}"
            )
            if self.protocol["tipo_calculo"] == "recipientes":
                self.summary.setText(
                    f"{n} {params['recipiente']}\n"
                    + self.summary.text()
                    + "\n"
                    + " ".join(plan["pendencias_preparo"])
                )
            if not self.prepare_chart(params, plan):
                return
            ax = self.figure.add_subplot(111)
            x = sorted({round(n * i / 20) for i in range(21)})
            ax.plot(x, [v * i for i in x], label="Volume base", color="#315e5b")
            if e > 0:
                ax.plot(
                    x,
                    [v * i * (1 + e / 100) for i in x],
                    label="Com excedente",
                    linestyle="--",
                    color="#315e5b",
                )
            ax.scatter([n], [r["quantidade_final"]], color="#315e5b")
            from matplotlib.ticker import MaxNLocator

            ax.xaxis.set_major_locator(MaxNLocator(integer=True))
            ax.set_xlabel(
                "Número de " + params["recipiente"]
                if self.protocol["tipo_calculo"] == "recipientes"
                else "Número total de unidades"
            )
            ax.set_ylabel(f"Volume ({unit})")
            ax.set_title(f"Volume por unidade: {v:g} {unit}; excedente: {e:g}%")
            ax.legend()
            self.canvas.draw_idle()
            self.updated.emit(params, plan)
            return
        if self.protocol["tipo_calculo"] == "seriada":
            preencher_serie(self.serie_table, plan)
            self.summary.setText(
                f"Alíquota por transferência: {plan['resultado']['quantidade_reagente']:.6g} mL. {plan['observacao_diluicao']}\n{plan['solvente']}"
            )
            if not self.prepare_chart(params, plan):
                return
            ax = self.figure.add_subplot(111)
            x = list(range(len(plan["etapas"]) + 1))
            y = [params["concentracao_inicial"]] + [
                step["concentracao"] for step in plan["etapas"]
            ]
            ax.plot(x, y, marker="o", color="#315e5b")
            ax.set_yscale("log")
            import math

            lower = min(y) / 1.1
            if lower == 0:
                lower = min(y)
            upper = max(y) * 1.1
            ax.set_ylim(lower, upper if math.isfinite(upper) else max(y))
            from matplotlib.ticker import MaxNLocator

            ax.xaxis.set_major_locator(MaxNLocator(integer=True))
            ax.set_xlabel("Etapa (0 = estoque)")
            ax.set_ylabel(
                f"Concentração ({params['unidade_concentracao']}) · escala log"
            )
            ax.set_title(f"Fator por etapa: {params['fator']:g}")
            self.canvas.draw_idle()
            self.updated.emit(params, plan)
            return
        r = plan["resultado"]
        label_issues = (
            "\n" + " ".join(plan["erros_rotulo"].values())
            if plan.get("erros_rotulo")
            else ""
        )
        dilution = self.protocol["tipo_calculo"] in {"diluicao", "fator"}
        dose_label = "Alíquota de estoque" if dilution else "Reagente comercial"
        detail = (
            f"\nFator de diluição: {r['fator_diluicao']:.6g}. {plan['observacao_diluicao']}"
            if dilution
            else ""
        )
        self.summary.setText(
            f"{dose_label}: {r['quantidade_reagente']:.6g} {r['unidade_reagente']}\nSolvente/diluente: {plan['solvente']}{detail}{label_issues}"
        )
        if not self.prepare_chart(params, plan):
            return
        ax = self.figure.add_subplot(111)
        quantity = r["quantidade_final"]
        if self.protocol["tipo_calculo"] == "fator":
            a = params["volume_alicota"]
            c0 = params["concentracao_inicial"]
            xmax = max(quantity, a * 2)
            x = [a + (xmax - a) * i / 20 for i in range(21)]
            y = [c0 * (a / v) for v in x]
            ax.plot(x, y, color="#315e5b")
            ax.scatter([quantity], [r["concentracao_calculada"]], color="#315e5b")
            ax.set_xlabel("Volume final de solução (mL)")
            ax.set_ylabel(f"Concentração final ({params['unidade_concentracao']})")
            ax.set_title(
                f"Estoque e alíquota fixos: {c0:g} {params['unidade_concentracao']}; {a:g} mL"
            )
            self.canvas.draw_idle()
            self.updated.emit(params, plan)
            return
        x = [quantity * i / 20 for i in range(21)]
        y = [v * (r["quantidade_reagente"] / quantity) for v in x]
        ax.plot(x, y, color="#315e5b")
        ax.scatter([quantity], [r["quantidade_reagente"]], color="#315e5b")
        ax.set_xlabel(f"Quantidade final de solução ({r['unidade_final']})")
        ax.set_ylabel(f"{dose_label} ({r['unidade_reagente']})")
        unit = (
            "mol/L"
            if self.protocol["tipo_calculo"] == "molar"
            else params["unidade_concentracao"]
            if self.protocol["tipo_calculo"] in {"estoque", "diluicao"}
            else f"% {params['base']}"
        )
        ax.set_title(f"Concentração fixa: {params['concentracao']:g} {unit}")
        self.canvas.draw_idle()
        self.updated.emit(params, plan)
