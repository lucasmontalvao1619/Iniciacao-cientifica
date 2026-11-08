"""POPs e fichas de implantação com fontes e ilustrações identificadas."""

from io import BytesIO
from pathlib import Path


def pop_sections(protocol):
    if protocol.get("tipo_calculo") == "desidratado":
        source = protocol["fontes"][0]
        return [
            ("Identificação", f"{protocol['id']} · {protocol['name']}"),
            (
                "Finalidade",
                "Calcular massa nominal de um meio comercial desidratado pela proporção indicada na instrução do produto. A orientação técnica geral vem da Anvisa; os dados particulares do fabricante são declarados pelo pesquisador e não verificados automaticamente.",
            ),
            (
                "Perguntas ao pesquisador",
                "Qual produto será preparado? Qual massa em g e volume de referência em mL constam na instrução? Esse volume se refere à água ou ao volume final? Qual volume correspondente deseja preparar? Qual rótulo/documento e versão fundamentam os dados? Quando o consultou, se conhecido? Qual procedimento, pH, processo/ciclo, suplementos e conservação/validade são exigidos? Identidade do produto é opcional para o cálculo; condições ausentes ficam pendentes.",
            ),
            (
                "Cálculo e convenção",
                "Fator = volume alvo/volume de referência. Massa alvo = massa de referência × fator. Todos os números são positivos e finitos; volumes expressos em mL e massas em g. Se a instrução define volume de água, escalar a água correspondente, sem apresentá-la como volume final exato. Somente quando define volume final usar a indicação q.s.p. Não adotar uma concentração universal para produtos com nomes semelhantes.",
            ),
            (
                "Materiais e procedimento",
                "Balança e instrumentos volumétricos de faixa/tolerância adequadas, recipientes e equipamentos compatíveis com a instrução.\n1. Conferir produto e documento/versão informados.\n2. Transcrever massa, volume e convenção da instrução; calcular e conferir a massa alvo.\n3. Pesar e hidratar conforme o fabricante, preservando a distinção entre água e volume final.\n4. Seguir a sequência e as condições de preparo, processo/ciclo, suplementos, pH e conservação indicados para o produto e método. Não presumir um ciclo ou prazo universal.\n5. Conferir controle de qualidade e requisitos do meio antes do uso.",
            ),
            (
                "Resultados e limites",
                "Plano mostra massa, água ou volume final e condições declaradas. Gráfico mostra a massa em função do volume na convenção selecionada e atualiza com a edição. Não valida composição, fabricante, instrução, suplementos, esterilização ou estabilidade. Sem medições simuladas ou validação em bancada.",
            ),
            (
                "Fonte das regras",
                f"{source['title']}. {source['organization']}, {source['year']}. ISBN: {source['isbn']}.\nP. 7–8 e 11 (PDF 9–10 e 13): pesagem/hidratação e instruções do fabricante. A introdução menciona ciclo normalmente 121 °C/15 min, mas exige observar o fabricante; isso não é aplicado como regra universal. Escala proporcional e convenção de volume são explicitações da implementação.\n{source['url']}",
            ),
            (
                "Rastreabilidade",
                f"PDF obtido em: {source['obtido_em']}\nConsulta PREP-009: {source['consultado_em']}\nSHA-256: {source['sha256']}\n{source['papel']}",
            ),
        ]
    if protocol.get("tipo_calculo") == "formula":
        source = protocol["fontes"][0]
        recipe = protocol["formulacoes"][0]
        return [
            ("Identificação", f"{protocol['id']} · {protocol['name']}"),
            (
                "Finalidade",
                "Escalonar ingredientes de uma formulação para um volume nominal de referência, mantendo unidades e origem. Há uma receita identificada da fonte e uma opção separada de autoria do pesquisador; receitas livres não são validadas automaticamente pela Anvisa.",
            ),
            (
                "Perguntas ao pesquisador",
                "Qual formulação será usada? Qual volume nominal deseja preparar? Para receita própria, qual volume de referência, componentes, quantidades, unidades e fonte/versão ou autoria a fundamentam? Qual procedimento, pH e condição de medida, processo/ciclo de esterilização e conservação/validade se aplicam? Condições ausentes ficam pendentes; não presumir um ciclo ou prazo universal.",
            ),
            (
                "Formulação de referência",
                "Ágar nutriente, Anvisa 2013, p. 15: extrato de carne 3 g; peptona 5 g; ágar 15 g; água destilada 1000 mL. pH 6,8 ± 0,2 a 25 °C. Para essa receita, a fonte indica conservar embalado de 4 a 8 °C por até 3 meses; conferir condições locais, sem calcular automaticamente uma data. A água permanece como componente da receita; não reinterpretar automaticamente como q.s.p. ao volume final. A alternativa do pesquisador é identificada separadamente e pode conter componentes em g, mg, mL e µL.",
            ),
            (
                "Cálculo",
                "Fator de escala = volume nominal planejado / volume nominal de referência. Multiplicar cada quantidade pelo fator, preservando sua unidade. Não somar massas e volumes nem converter sólidos em volumes. Os valores e resultados devem ser positivos e finitos; o nome distingue cada ingrediente. A escala não garante volume final exato após dissolução nem equivalência entre formulações.",
            ),
            (
                "Materiais e procedimento",
                f"Balança e instrumentos volumétricos adequados aos componentes, recipientes e equipamento de esterilização compatíveis com o método.\n1. Conferir origem e formulação.\n2. Calcular e medir os componentes nas unidades indicadas.\n3. Para a receita de referência: {recipe['procedimento']}\n4. Conferir o pH e as condições de medida. Informar o processo/ciclo definido para o meio e a carga; não adotar automaticamente 121 °C/15 min.\n5. Conferir controle de qualidade, conservação e validade pelo método antes do uso.",
            ),
            (
                "Resultados e limites",
                "Tabela exibe todas as quantidades planejadas. O gráfico permite escolher um componente e mostra sua quantidade por volume nominal, sem misturar g com mL. Edição de receita própria mantém sua atribuição ao pesquisador. Sem verificação automática de compatibilidade, eficácia do ciclo ou estabilidade e sem validação em bancada. O controle de qualidade do meio continua necessário.",
            ),
            (
                "Fonte das regras",
                f"{source['title']}. {source['organization']}, {source['year']}. ISBN: {source['isbn']}.\nP. 14–15, fórmula na p. 15 (PDF 17). O escalonamento proporcional e a separação de receitas livres são adaptações explícitas da implementação.\n{source['url']}",
            ),
            (
                "Rastreabilidade",
                f"PDF obtido em: {source['obtido_em']}\nConsulta PREP-008: {source['consultado_em']}\nSHA-256: {source['sha256']}\n{source['papel']}",
            ),
        ]
    if protocol.get("tipo_calculo") == "recipientes":
        sources = protocol["fontes"]
        return [
            ("Identificação", f"{protocol['id']} · {protocol['name']}"),
            (
                "Finalidade",
                "Dimensionar meio de composição já definida para placas ou tubos. Planejar um tipo de recipiente e uma dose por vez, incluindo controles e repetições na contagem. Valores planejados não são medições nem comprovação de preparo.",
            ),
            (
                "Perguntas ao pesquisador",
                "Usará placas ou tubos? Qual formato/capacidade será usado? Qual volume cada recipiente receberá e em qual unidade: µL, mL ou L? Quantos recipientes receberão o meio, incluindo controles e repetições? Qual percentual acrescentar ao volume base? Zero significa sem reserva. Qual meio e qual método orientam o volume, preparo e distribuição? Identificações e método são opcionais no cálculo; ausências ficam pendentes para conferência antes de executar. Nenhuma dose é preenchida automaticamente.",
            ),
            (
                "Cálculos",
                "Volume base = número de recipientes × volume por recipiente. Reserva = base × percentual/100. Total = base × (1 + percentual/100). Contagem inteira positiva, volume positivo e finito, percentual finito e não negativo. A reserva não aumenta a dose individual. O percentual é acréscimo sobre a base, não fração perdida do total. Unidades devem ser coerentes; trocar a unidade na interface não converte os números.",
            ),
            (
                "Materiais e procedimento",
                "1. Identificar meio, método e recipientes compatíveis. Conferir dose, formato/capacidade e número de recipientes, já incluindo controles e repetições.\n2. Definir reserva conforme necessidades reais e conferir base, reserva e total.\n3. Preparar o meio pelo método/formulação ou pela instrução do produto, com instrumento adequado ao volume e à tolerância requerida. O balão ilustrado exemplifica vidraria, sem impor marca, capacidade ou técnica universal para meios.\n4. Conferir requisitos de esterilidade e condições de preparo/distribuição do método; distribuir a dose informada por recipiente. Não adotar temperaturas/ciclos/validade universais nem aumentar a dose para consumir a reserva.",
            ),
            (
                "Gráfico e limites",
                "O gráfico mostra volume por número de recipientes, com dose e percentual fixos; permite editar e recalcular. Não são observações experimentais. Dose e condições dependem do meio e do recipiente; capacidade nominal não é dose recomendada. Não calcula massa de pó, suplementos, estabilidade, ciclo ou data de validade. Grupos de meios/doses diferentes exigem planejamentos separados. Sem validação em bancada.",
            ),
            (
                "Fontes e adaptação",
                "Anvisa 2013, módulo 5, p. 18 (PDF 20): exemplo de distribuição de ágar chocolate em placas de 90 mm ou tubos, com doses específicas diferentes; não generalizar essas doses ou condições para qualquer meio. MS 2016, p. 48 (PDF 49): dimensionamento e reserva específicos de reações. O produto N × v e a reserva percentual são derivações matemáticas explícitas do software, sem importar margem positiva automática.\n"
                + "\n\n".join(
                    f"{s['title']}. {s['organization']}, {s['year']}.\n{s['url']}"
                    for s in sources
                ),
            ),
            (
                "Rastreabilidade",
                "\n\n".join(
                    f"{s['id']}\nObtido em: {s['obtido_em']}\nConsulta PREP-010: {s['consultado_em']}\nSHA-256: {s['sha256']}\n{s['papel']}"
                    for s in sources
                ),
            ),
        ]
    if protocol.get("tipo_calculo") == "volume":
        source = protocol["fontes"][0]
        return [
            ("Identificação", f"{protocol['id']} · {protocol['name']}"),
            (
                "Finalidade",
                "Dimensionar um volume de composição já definida pelo método, para várias unidades e uma reserva escolhida pelo pesquisador. Não determina uma formulação nem aumenta a dose de cada unidade.",
            ),
            (
                "Perguntas ao pesquisador",
                "Qual é o volume v por unidade? Qual unidade de volume será usada: µL, mL ou L? Quantas unidades N receberão esse volume, incluindo os controles e repetições pertinentes? Qual percentual E acrescentar à base? Zero significa sem excedente. Qual material será distribuído? A identificação é opcional. Volume e quantidade de unidades começam sem resposta; nenhuma margem positiva é adotada automaticamente.",
            ),
            (
                "Cálculos",
                "Volume base = v × N. Reserva = volume base × E/100. Total a preparar = volume base × (1+E/100). O percentual é acréscimo sobre a base, não uma fração perdida do total preparado. N já deve incluir todas as unidades, sem multiplicar controles ou repetições novamente. Valores usam a unidade selecionada, sem conversão automática. N deve ser inteiro positivo; v positivo e finito; E finito e não negativo.",
            ),
            (
                "Materiais e procedimento",
                "1. Conferir o volume por unidade e a composição estabelecidos pelo método. Contar todas as unidades que receberão esse volume.\n2. Definir a reserva conforme método, instrumentos e necessidades reais, inclusive zero se não houver excedente.\n3. Conferir base, reserva e total; escolher instrumentos e recipientes compatíveis com o volume e o material. A micropipeta ilustrada é apenas um exemplo para pequenos volumes.\n4. Preparar o total conforme o método e distribuir v por unidade. Não aumentar a dose para consumir a reserva.",
            ),
            (
                "Gráfico e limites",
                "O gráfico compara volume base e total por número de unidades, com v e E fixos. Não representa medições ou comprovação de perdas. Não define margem universal, composição, concentração, armazenamento ou tolerância instrumental. Limite da interface: um milhão de unidades. Sem validação em bancada.",
            ),
            (
                "Fonte e adaptação",
                f"{source['title']}. {source['organization']}, {source['year']}, {source['edition']}. ISBN {source['isbn']}.\nP. 48 (PDF 49): dimensionamento por número de reações e reserva por perdas em método específico. A calculadora percentual é uma generalização matemática explícita; não transfere a regra específica +1/+2 reações para todo experimento.\n{source['url']}",
            ),
            (
                "Rastreabilidade",
                f"PDF obtido em: {source['obtido_em']}\nConsulta PREP-007: {source['consultado_em']}\nSHA-256: {source['sha256']}\n{source['papel']}",
            ),
        ]
    if protocol.get("tipo_calculo") == "fator":
        source = protocol["fontes"][0]
        return [
            ("Identificação", f"{protocol['id']} · {protocol['name']}"),
            (
                "Finalidade",
                "Calcular fator de diluição e concentração final a partir de concentração do estoque, alíquota e volume final informados pelo pesquisador. Valores planejados não são medições nem comprovação de execução.",
            ),
            (
                "Perguntas ao pesquisador",
                "Qual é a concentração inicial C1 e sua unidade por volume? Qual alíquota V1 em mL será transferida? Qual é o volume FINAL V2 em mL? Como estoque e diluente serão identificados? As identificações são opcionais para o cálculo; os números essenciais começam sem resposta. Não informar o volume de diluente no lugar do volume final.",
            ),
            (
                "Cálculos",
                "Pela conservação C1 × V1 = C2 × V2, calcular fator F = V2/V1 e concentração final C2 = C1 × (V1/V2). A unidade da concentração final é a mesma da inicial. V1 não pode superar V2; igualdade significa fator 1, sem diluição. V2 − V1 é diferença nominal, não dose exata de diluente. Rejeitar entradas não positivas, não finitas ou fora da faixa numérica. Percentual massa/massa não se aplica a esta fórmula volumétrica.",
            ),
            (
                "Materiais",
                "Estoque de concentração conhecida e diluente compatível. Instrumento volumétrico adequado à alíquota e à tolerância requerida; balão ou vidraria compatível com o volume final. A imagem ilustra equipamento e não impõe marca ou capacidade.",
            ),
            (
                "Procedimento",
                "1. Conferir concentração real do estoque, unidade, compatibilidade do diluente e requisitos do método.\n2. Informar alíquota e volume final, conferir fator e concentração calculados.\n3. Transferir a alíquota com instrumento adequado e completar com diluente q.s.p. ao volume final, nas condições do método. Não somar volumes supondo aditividade exata.\n4. Homogeneizar e identificar conforme a substância e o método.",
            ),
            (
                "Gráfico e limites",
                "O gráfico varia volume final, mantendo concentração inicial e alíquota fixas; o ponto marca o preparo informado. Não representa medições ou análise estatística. Não verifica solubilidade, estabilidade, alteração de atividade, tolerância de equipamento ou adequação clínica. As unidades são referidas à mesma substância/atividade, sem conversão automática. Sem validação em bancada.",
            ),
            (
                "Fonte das regras",
                f"{source['title']}. {source['organization']}, {source['year']}. ISBN {source['isbn']}.\nP. 232: equação e conservação; p. 230–231: preparo e aferição. F=V2/V1 e C2=C1×V1/V2 são rearranjos explícitos da implementação.\n{source['url']}",
            ),
            (
                "Rastreabilidade",
                f"PDF obtido em: {source['obtido_em']}\nConsulta para PREP-006: {source['consultado_em']}\nSHA-256: {source['sha256']}\n{source['papel']}",
            ),
        ]
    if protocol.get("tipo_calculo") == "seriada":
        sources = protocol["fontes"]
        return [
            ("Identificação", f"{protocol['id']} · {protocol['name']}"),
            (
                "Finalidade",
                "Planejar uma sequência volumétrica de fator constante, com concentrações calculadas e volumes remanescentes após transferências. Não inclui preparo de amostra sólida, contagem de colônias nem cultivo.",
            ),
            (
                "Perguntas ao pesquisador",
                "Qual é a concentração do estoque C0 e sua unidade por volume? Qual fator F maior que 1 deseja entre as diluições? Quantas diluições N serão feitas, sem contar o estoque? Qual volume V em mL será preparado em cada etapa antes da transferência seguinte? Deseja retirar uma alíquota também do último recipiente para igualar os volumes? Qual estoque e diluente serão usados? As identificações são opcionais no cálculo; números essenciais começam sem resposta.",
            ),
            (
                "Cálculos e convenções",
                "A primeira diluição é etapa 1: Ck = C0/F^k. Alíquota de transferência a = V/F. Diluente nominal por etapa = V − a. Após transferir ao próximo, restam V − a nos intermediários. O último mantém V, ou V − a se o pesquisador escolher a retirada final. A retirada não altera a concentração da solução homogeneizada. A tabela mostra concentrações, fatores acumulados, alíquotas e volumes restantes; o gráfico usa escala logarítmica e identifica o estoque como etapa 0.",
            ),
            (
                "Materiais",
                "Estoque e diluente compatíveis. N recipientes adequados ao volume V e ao método. Instrumento volumétrico com faixa e tolerância compatíveis com a alíquota; pipeta ou ponteira nova para cada transferência. O balão ilustrado exemplifica vidraria volumétrica, sem impor marca ou capacidade.",
            ),
            (
                "Procedimento",
                "1. Conferir estoque, diluente, concentração, unidade e requisitos do método. Identificar N recipientes.\n2. Preparar cada diluição com a alíquota calculada e diluente conforme o método, com volume nominal V. Homogeneizar antes de retirar a alíquota para o recipiente seguinte.\n3. Repetir sucessivamente com material de transferência adequado e novo.\n4. No último recipiente, manter o volume ou retirar uma alíquota final, conforme escolha explícita, com destinação definida pelo método.\n5. Conferir os volumes restantes antes de outras retiradas e identificar as soluções.",
            ),
            (
                "Limites",
                "Volumes nominais pressupõem mistura compatível e não garantem aditividade exata. Seguir aferição e condições térmicas do método. Este planejamento conserva soluto/atividade e não calcula decaimento ou instabilidade. Não generalizar salina, incubação ou aplicações micológicas da fonte. Limite da interface: 100 diluições, sem contar estoque. Não há validação em bancada; gráfico de planejamento, sem observações simuladas.",
            ),
            (
                "Fontes das regras",
                "Fiocruz v. 1, 2009, p. 232: relação de diluição e sequência gráfica. Fiocruz v. 4, copyright 2010, p. 441–442: transferências sucessivas e homogeneização. Fórmulas de volume restante e opção de igualar o último são derivações/decisões explícitas da implementação.\n"
                + "\n\n".join(
                    f"{s['title']}. {s['organization']}, {s['year']}. ISBN: {s['isbn']}.\n{s['url']}"
                    for s in sources
                ),
            ),
            (
                "Rastreabilidade",
                "\n\n".join(
                    f"{s['id']}\nObtido em: {s['obtido_em']}\nConsulta PREP-005: {s['consultado_em']}\nSHA-256: {s['sha256']}\n{s.get('nota_bibliografica', '')}\n{s['papel']}"
                    for s in sources
                ),
            ),
        ]
    if protocol.get("tipo_calculo") == "diluicao":
        source = protocol["fontes"][0]
        return [
            ("Identificação", f"{protocol['id']} · {protocol['name']}"),
            (
                "Finalidade",
                "Planejar uma diluição volumétrica de solução-estoque, conservando a quantidade de soluto transferida. O cálculo fornece a alíquota de estoque e o volume final a completar; as substâncias e as condições de preparo são definidas para o experimento.",
            ),
            (
                "Perguntas para o cálculo",
                "Qual é a concentração do estoque C1? Qual concentração final C2 deseja? Em qual unidade comum por volume ambas serão expressas? Qual é o volume final V2 em mL? Como o estoque e o diluente serão identificados? A identificação é opcional para o cálculo numérico. Não usar percentual massa/massa nesta equação volumétrica.",
            ),
            (
                "Cálculos",
                "C1 × V1 = C2 × V2; portanto V1 = V2 × C2/C1. C1 e C2 devem usar a mesma unidade, referida à mesma substância ou atividade. O fator de diluição é C1/C2. V2 − V1 é uma diferença nominal, não uma medida exata de diluente a adicionar. C2 maior que C1 não pode ser obtida por diluição; igualdade significa fator 1, sem diluição. Todos os valores devem ser positivos e finitos.",
            ),
            (
                "Materiais",
                "Solução-estoque de concentração conhecida e diluente compatível. Pipeta ou instrumento volumétrico com faixa e tolerância adequadas à alíquota; recipiente de transferência e balão volumétrico adequados ao volume final. O exemplo de equipamento ilustrado não determina uma marca ou capacidade obrigatória.",
            ),
            (
                "Procedimento",
                "1. Conferir concentração real do estoque, FDS, compatibilidade do diluente, unidades e requisitos do método.\n2. Calcular V1 e escolher instrumento adequado ao volume e à tolerância requerida.\n3. Transferir a alíquota para a vidraria, na sequência e nas condições térmicas definidas pelo método.\n4. Completar com diluente q.s.p. ao volume final; ler a aferição evitando paralaxe. Não substituir esse ajuste pela subtração dos volumes.\n5. Homogeneizar e identificar a solução conforme o método da substância.",
            ),
            (
                "Limites",
                "Dimensionamento nominal, sem validação em bancada. Não verifica solubilidade, estabilidade, alterações de atividade, precisão do instrumento ou efeitos térmicos. O gráfico representa dimensionamento, não dados medidos. Unidades disponíveis: mg/mL, µg/mL, g/L, mol/L, mmol/L, U/mL, % m/v e % v/v; não há conversão automática entre as concentrações. % v/v não pode superar 100%.",
            ),
            (
                "Fonte das regras",
                f"{source['title']}. {source['organization']}, {source['year']}. ISBN {source['isbn']}.\nP. 230–231: materiais, transferência e q.s.p.; p. 232: conservação do soluto e equação de diluição. As restrições de unidade e a diferença nominal são explicitações dimensionais da implementação.\n{source['url']}",
            ),
            (
                "Rastreabilidade",
                f"PDF obtido em: {source['obtido_em']}\nConsulta para PREP-004: {source['consultado_em']}\nSHA-256: {source['sha256']}\n{source['papel']}",
            ),
        ]
    if protocol.get("tipo_calculo") == "estoque":
        sources = protocol["fontes"]
        return [
            ("Identificação", f"{protocol['id']} · {protocol['name']}"),
            (
                "Finalidade",
                "Dimensionar uma solução-estoque de concentração nominal definida para uso posterior. O pesquisador escolhe as substâncias e responde às perguntas aplicáveis; o programa não identifica automaticamente o reagente nem atribui condições universais de conservação.",
            ),
            (
                "Perguntas para o cálculo",
                "Em qual unidade o estoque será expresso: mg/mL, µg/mL, g/L, mol/L ou U/mL? Qual concentração e volume final deseja? O reagente será pesado ou medido por volume? A correção usa teor químico % m/m, potência certificada µg/mg ou atividade U/mg? Se precisar converter U em µg, qual equivalência específica consta na referência do reagente? Para mol/L, qual é a massa molar da forma química real? Para medição volumétrica do reagente comercial, qual é sua densidade em g/mL?",
            ),
            (
                "Cálculos",
                "Para concentração massiva e teor químico: massa pura = concentração × volume final, com unidades coerentes; massa comercial = massa pura/(teor/100). Para mol/L, n = C × V em litros e massa pura = n × massa molar. Para potência: massa em mg = V em mL × C em µg/mL / P em µg/mg. Para atividade: massa em mg = V em mL × C em U/mL / atividade em U/mg. Se o objetivo estiver em µg/mL e o certificado em U/mg, perguntar a equivalência específica e em U/µg: potência µg/mg = atividade U/mg / e. Não existe fator universal U/µg. Se o reagente for medido por volume: V comercial = massa comercial em g / densidade comercial em g/mL.",
            ),
            (
                "Materiais e líquidos",
                "Balança adequada à massa calculada ou instrumento volumétrico apropriado, material de transferência, vidraria compatível com o volume e frasco adequado à substância. Solvente de dissolução e diluente final podem ser diferentes; o campo de diluente vazio indica usar o solvente informado. Se as identidades não forem fornecidas, o cálculo não as presume.",
            ),
            (
                "Procedimento",
                "1. Conferir a base de concentração e o dado correspondente do rótulo/certificado; teor químico e potência não são intercambiáveis.\n2. Calcular a dose corrigida e medir com instrumento apropriado.\n3. Dissolver no solvente e nas condições definidas pelo método da substância.\n4. Completar ao volume final com o diluente indicado, sem tratar volumes como aditivos.\n5. Homogeneizar, identificar o frasco e estabelecer conservação e validade conforme método/estabilidade, antes do uso.",
            ),
            (
                "Perguntas de identificação e conservação",
                "Como o frasco será identificado? Qual é o lote do reagente? Quem preparará? Qual data de preparo foi prevista? Qual validade foi definida e em qual método se baseia? Quais condições de armazenamento se aplicam? Esses dados são opcionais durante o planejamento; os ausentes ficam registrados como pendentes. O programa não calcula uma data de validade nem define automaticamente refrigeração, proteção da luz ou material do frasco.",
            ),
            (
                "Limites",
                "Dimensionamento nominal, sem validação em bancada. Conferir solubilidade, compatibilidade, precisão de medição e requisitos do experimento. Dados de potência/atividade devem corresponder ao certificado do lote e às unidades escolhidas. A fonte Anvisa trata de antimicrobianos; suas condições específicas de conservação não são generalizadas para qualquer estoque.",
            ),
            (
                "Fontes das regras",
                "Fiocruz 2009, p. 226–234: concentrações, pureza, preparo, identificação e conservação. Anvisa 2020, módulo 10, p. 110–111: massa corrigida por potência e distinção de solvente/diluente. O pareamento de unidades e a conversão condicionada a uma equivalência fornecida pelo pesquisador são adaptações dimensionais explícitas, sem copiar um fator U/µg de um composto para outros.\n"
                + "\n\n".join(
                    f"{source['title']}. {source['organization']}, {source['year']}. ISBN {source['isbn']}.\n{source['url']}"
                    for source in sources
                ),
            ),
            (
                "Rastreabilidade",
                "\n\n".join(
                    f"{source['id']}\nObtido em: {source['obtido_em']}\nConsulta para PREP-003: {source['consultado_em']}\nSHA-256: {source['sha256']}\n{source['papel']}"
                    for source in sources
                ),
            ),
        ]
    if protocol.get("tipo_calculo") == "molar":
        source = protocol["fontes"][0]
        return [
            ("Identificação", f"{protocol['id']} · {protocol['name']}"),
            (
                "Finalidade",
                "Preparar solução de concentração molar formal definida, a partir de reagente pesado ou líquido de teor e densidade conhecidos, com soluto e solvente escolhidos para o experimento.",
            ),
            (
                "Parâmetros e cálculos",
                "Informar concentração C em mol/L, volume final V em mL, massa molar MM em g/mol e teor T em % m/m. Quantidade de matéria n = C × V/1000; massa pura = n × MM; massa comercial = massa pura/(T/100). Se o reagente for medido por volume, fornecer sua densidade d em g/mL: volume comercial = massa comercial/d. Não usar densidade do solvente no lugar da densidade do reagente.",
            ),
            (
                "Identidade e teor",
                "A massa molar e o teor devem se referir à forma química real do rótulo, incluindo hidratação quando aplicável. A massa molar é fornecida pelo pesquisador; não é inferida do nome. Este cálculo não converte teor % v/v em % m/m e não calcula concentrações de íons, atividades ou solubilidade.",
            ),
            (
                "Materiais e reagentes",
                "Reagente e solvente compatíveis com o método. Balança calibrada, recipiente de pesagem e utensílios de transferência para reagente pesado; pipeta adequada para líquido medido por volume. Balão volumétrico de capacidade e precisão correspondentes ao preparo, conforme Fiocruz p. 230.",
            ),
            (
                "Procedimento",
                "1. Conferir rótulo, massa molar, teor, FDS e requisitos do experimento.\n2. Calcular a quantidade de reagente, corrigindo o teor m/m; para medição volumétrica, usar também sua densidade.\n3. Medir e transferir quantitativamente. Dissolver ou misturar em parte do solvente respeitando a sequência e as condições de segurança do método.\n4. Completar com solvente q.s.p. ao volume final no balão volumétrico, nas condições térmicas do método. Não subtrair volumes como se fossem aditivos.\n5. Homogeneizar, identificar e verificar a necessidade de padronização; armazenamento e estabilidade dependem do reagente e do experimento.",
            ),
            (
                "Limites",
                "Não há validação em bancada demonstrada. O dimensionamento não substitui verificação de solubilidade, compatibilidade, estabilidade, esterilidade ou padronização quando exigida. Para líquidos, o volume de reagente não pode superar o volume final: esta rotina não concentra soluções por remoção de solvente.",
            ),
            (
                "Fonte das regras",
                f"{source['title']}. {source['organization']}, {source['year']}. ISBN {source['isbn']}.\nP. 226: molaridade e massa molar; p. 229–232: teor, materiais e preparo; p. 249–250: exemplo de correção por teor m/m e densidade.\n{source['url']}",
            ),
            (
                "Rastreabilidade",
                f"PDF obtido em: {source['obtido_em']}\nConsulta/extração para PREP-002: {source['consultado_em']}\nSHA-256: {source['sha256']}\n{source['papel']}",
            ),
        ]
    if protocol.get("tipo_calculo") == "percentual":
        source = protocol["fontes"][0]
        return [
            ("Identificação", f"{protocol['id']} · {protocol['name']}"),
            (
                "Finalidade",
                "Dimensionar soluções percentuais com soluto e solvente definidos pelo pesquisador, nas bases massa/volume, volume/volume ou massa/massa.",
            ),
            (
                "Parâmetros e cálculos",
                "Informar base, concentração C (%), quantidade final Q, soluto, solvente e teor T (%). Para m/v, Q em mL e reagente em g; v/v, ambos em mL; m/m, ambos em g. Quantidade do reagente comercial = C × Q / T. Teor T em % m/m nas bases m/v e m/m, e em % v/v na base v/v. Não converter entre bases de teor sem dados adicionais.",
            ),
            (
                "Materiais e reagentes",
                "Soluto, solvente, recipiente graduado compatível e utensílios para transferência. Para sólidos: balança calibrada/nivelada, recipiente de pesagem e espátula; para líquidos: pipeta adequada. A seleção final depende da quantidade, compatibilidade e precisão do experimento.",
            ),
            (
                "Procedimento",
                "1. Conferir o rótulo, teor, FDS, compatibilidade e solubilidade.\n2. Calcular e medir a quantidade de reagente com instrumentos adequados.\n3. Transferir quantitativamente e dissolver ou misturar em parte do solvente conforme as condições do experimento.\n4. Completar à quantidade final. Para volumes, usar solvente q.s.p.; não presumir aditividade de volumes. Para m/m, a massa final inclui reagente comercial e solvente.\n5. Homogeneizar e identificar. Estabilidade, armazenamento e condições especiais devem ser definidos pelo experimento e pelas substâncias.",
            ),
            (
                "Limites",
                "O cálculo não verifica automaticamente solubilidade, compatibilidade química, esterilidade, estabilidade, condições de dissolução ou adequação clínica. O POP geral deve ser conferido com o método do experimento e as FDS. Não há validação em bancada demonstrada.",
            ),
            (
                "Fonte das regras",
                f"{source['title']}. {source['organization']}, {source['year']}. ISBN {source['isbn']}.\nP. 227: bases percentuais; p. 229: pureza; p. 230–232: materiais e preparo. A correção algébrica pelo teor e a regra de q.s.p. são adaptações explícitas do software.\n{source['url']}",
            ),
            (
                "Rastreabilidade",
                f"Obtenção: {source['obtido_em']}\nConsulta/extração: {source['consultado_em']}\nSHA-256 do PDF: {source['sha256']}\n{source['papel']}",
            ),
        ]
    return [
        (
            "Identificação",
            f"{protocol['id']} · {protocol['name']}\nAplicação: {protocol['application']}",
        ),
        (
            "Situação",
            f"{protocol['status']}\nFicha de implantação; procedimento operacional ainda não disponível.",
        ),
        ("Finalidade", protocol["name"]),
        (
            "Materiais e reagentes",
            "Lista, especificações e quantidades pendentes de conferência nas fontes primárias.",
        ),
        (
            "Procedimento",
            f"O procedimento de {protocol['name']} ainda não está registrado como POP operacional. Conferir etapas, condições, unidades, cálculos, controles e limitações antes de disponibilizar instruções de execução.",
        ),
        (
            "Origem do cadastro",
            f"{protocol['origem']}\n{protocol['localizacao']}\n{protocol['url']}",
        ),
        (
            "Referências indicadas",
            f"{protocol['source_codes']}\n{protocol['consulta_fontes_primarias']}",
        ),
        (
            "Rastreabilidade",
            f"Consulta ao catálogo: {protocol['consultado_em']}\nInclusão: {protocol['incluido_em']}\nFuso: {protocol['fuso']}\nEssas datas não comprovam consulta às fontes primárias.",
        ),
    ]


def pop_text(protocol):
    return (
        f"PROCEDIMENTO OPERACIONAL PADRÃO\n{protocol['id']} · {protocol['name']}\n\n"
        + "\n\n".join(
            f"{heading.upper()}\n{body}" for heading, body in pop_sections(protocol)
        )
    )


def write_pop_docx(protocol, path):
    # Load the document library only when exporting, preserving startup time.
    from docx import Document
    from docx.shared import Cm, Pt, RGBColor

    doc = Document()
    for border in doc.styles.element.xpath(".//w:pBdr"):
        border.getparent().remove(border)
    section = doc.sections[0]
    section.page_width, section.page_height = Cm(21), Cm(29.7)
    section.top_margin = section.bottom_margin = Cm(2)
    section.left_margin = section.right_margin = Cm(2.3)
    for name in ("Normal", "Title", "Heading 1"):
        style = doc.styles[name]
        style.font.name = "Arial"
        style.font.color.rgb = RGBColor(0, 0, 0)
    doc.styles["Normal"].font.size = Pt(10)
    doc.styles["Normal"].paragraph_format.space_after = Pt(6)
    doc.styles["Title"].font.size = Pt(20)
    doc.styles["Heading 1"].font.size = Pt(12)
    doc.add_paragraph("Procedimento operacional padrão", "Title")
    doc.add_paragraph(f"{protocol['id']} · {protocol['name']}")
    doc.add_paragraph(
        "Planejamento do protocolo identificado abaixo, com fontes e limites de aplicação. A situação de implementação é informada no documento."
    )
    for heading, body in pop_sections(protocol):
        doc.add_heading(heading, level=1)
        doc.add_paragraph(body)
    for image in protocol.get("images", []):
        doc.add_heading("Equipamento ilustrativo", level=1)
        doc.add_picture(
            str(Path(__file__).with_name("assets") / image["file"]),
            width=Cm(image.get("docx_width_cm", 7)),
        )
        doc.paragraphs[-1].paragraph_format.keep_with_next = True
        doc.add_paragraph(image["caption"]).paragraph_format.keep_with_next = True
        credit = doc.add_paragraph(
            f"Autor: {image['author']}. {image['license']}.\nFonte: {image['source']}\nObtida em: {image['obtido_em']}\n{image['changes']}\n{image['role']}"
        )
        credit.paragraph_format.keep_together = True
    buffer = BytesIO()
    doc.save(buffer)
    Path(path).write_bytes(buffer.getvalue())
