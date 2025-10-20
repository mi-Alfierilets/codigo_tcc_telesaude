from sqlalchemy import create_engine, Column, String, Integer, DateTime, Date, Boolean, ForeignKey, Text, Numeric, Time, SmallInteger
from sqlalchemy.orm import declarative_base, relationship, backref
from sqlalchemy import Enum
from datetime import datetime
import random
import uuid

DB_FILE = "tcc.db"
engine = create_engine(f"sqlite:///{DB_FILE}")
Base = declarative_base()


class Usuario(Base):
    #id do usuario
    __tablename__='USUARIO'
    id_usuario = Column(Integer, primary_key=True)
    #nome do usurio
    nome = Column(String(255), nullable=False)
    #email do usuario
    email = Column(String(255), unique=True, nullable=False)
    # senha
    senha = Column(String(255), nullable=False)
    #data do cadastro
    data_cadastro = Column(DateTime, default=datetime.utcnow)
    #data do nascimento do usuario
    data_de_nascimento = Column(Date)
    #coluna do RG do usuria
    RG=Column(String(20), unique=True, nullable=False)
    #coluna do CPF do usuario
    CPF=Column(String(20), unique=True, nullable=False)
    #genero do usuario, ja limitas as informaçoes colocada para faciliata no prenchimento do cadastro
    genero = Column(Enum(       "Feminino Cis",
                                "Masculino Cis",
                                "Feminino Trans",
                                "Masculino Trans",
                                "Não-binário",
                                "Outro",
                                "Prefiro não informar",
                                name='OPCOES_DE_GENERO'
                                ), 
                    nullable=False)
    #telefone do usuario
    telefone=Column(String(30), unique=True, nullable=False)
    #foto de perfil do usuario
    url_foto_perfil = Column(String(500))
    # Atributos de compliance (Política de Privacidade)
    termos_aceitos = Column(Boolean, default=False)
    data_aceite_termos = Column(DateTime)


    def __init__(self, email, senha, termos_aceitos=False, nome=None, data_de_nascimento=None, RG=None, CPF=None, genero=None, telefone=None, url_foto_perfil=None):
        self.nome = nome
        self.email = email
        self.senha = senha
        self.termos_aceitos = termos_aceitos
        self.data_de_nascimento = data_de_nascimento
        self.RG = RG
        self.CPF = CPF
        self.genero = genero
        self.telefone = telefone
        self.url_foto_perfil = url_foto_perfil
        if termos_aceitos:
            self.data_aceite_termos = datetime.utcnow()




    # Métodos (Lógica da Aplicação)
    def fazer_login(self, senha_informada):
    return self.senha == senha_informada # Simulação simples


class Endereco(Base):
    __tablename__ = 'ENDERECO'

    # Atributos (Colunas da Tabela)
    id_endereco = Column(Integer, primary_key=True)

    # Dados de endereço
    cep = Column(String(10), nullable=False)
    logradouro = Column(String(150), nullable=False)
    numero = Column(String(10), nullable=False)
    complemento = Column(String(50)) # Opcional
    bairro = Column(String(50), nullable=False)
    cidade = Column(String(50), nullable=False)
    estado = Column(String(2), nullable=False) # Ex: SP, RJ

    # -------------------------------------------------------------------------
    # Métodos de Lógica (Comportamento)
    # -------------------------------------------------------------------------

    def validar_cep(self):
        """
        Simula a validação do CEP com um serviço externo (como ViaCEP).
        Retornaria True/False se o CEP fosse encontrado.
        """
        return len(self.cep) in (8, 9) # 8 sem traço, 9 com traço

    def formatar_endereco(self):
        """ Retorna o endereço em um formato legível. """
        partes = [self.logradouro, self.numero, self.complemento]
        return ", ".join(p for p in partes if p) + f" - {self.cidade}/{self.estado}"



class Paciente(Base):
    __tablename__ = 'PACIENTE'

    # PK e FK para a tabela USUARIO
    id_paciente = Column(Integer, ForeignKey('USUARIO.id_usuario'), primary_key=True)

    # histrico medico do paciente

    historico_medico = Column(Text)

    # FK para Endereco
    endereco_id = Column(Integer, ForeignKey('ENDERECO.id_endereco'))

    # Relacionamento de volta para Usuario (para acessar email, senha, etc.)
    usuario = relationship('Usuario', backref=backref('paciente', uselist=False))

    def __init__(self, id_paciente):
        self.id_paciente = id_paciente

    def agendar_consulta(self, profissional_id, data, hora):
        # Lógica para criar um novo objeto Agendamento
        pass


class Profissional(Base):
    __tablename__ = 'PROFISSIONAL'
    __table_args__ = {'extend_existing': True}

    # 1. Chaves
    # PK e FK para a tabela USUARIO (Herança)
    id_profissional = Column(Integer, ForeignKey('USUARIO.id_usuario'), primary_key=True)

    # FK para Endereco
    endereco_id = Column(Integer, ForeignKey('ENDERECO.id_endereco'))

    # 2. Dados de Atuação e Registro

    # Tipo de Profissional (Enum para limitar opções)
    tipo_de_especialidade = Column(
        Enum(
            "Psicólogo",
            "Nutricionista",
            "Educador Físico",
            name='tipo_de_especialidade_options' # Corrected Enum definition
        ),
        nullable=False
    )

    # Agora armazena o número do conselho genérico (CRP, CRN, CREF)
    crp_cnr_cref= Column(String(30), nullable=False)

    # Indica se o registro (CRP/CRN/CREF) foi verificado
    crp_cnr_cref_verificado = Column(Boolean, default=False)

    #  Dados Específicos e Relacionamentos

    # Relacionamento de volta para Usuario (para acessar email, senha, etc.)
    usuario = relationship('Usuario', backref=backref('profissional', uselist=False))
    valor_consulta = Column(Numeric(10, 2), default=0.00)

    # Relacionamento 1:1 com DadosBancarios (Composição)
    # Lembre-se que 'DadosBancarios' precisa ser definido
    dados_bancarios = relationship('DadosBancarios', backref='profissional', uselist=False, cascade="all, delete-orphan")


    # -------------------------------------------------------------------------
    # Método Construtor (__init__)
    # -------------------------------------------------------------------------

    def __init__(self, id_profissional, tipo_de_especialidade, crp_cnr_cref, valor_consulta): # Added crp_cnr_cref
        self.id_profissional = id_profissional
        self.tipo_de_especialidade = tipo_de_especialidade
        self.crp_cnr_cref = crp_cnr_cref # Assigned the new parameter
        self.valor_consulta = valor_consulta


    # -------------------------------------------------------------------------
    # Métodos de Lógica (Comportamento)
    # -------------------------------------------------------------------------

    def solicitar_verificacao(self):
        """
        Simula o processo de verificação do registro no conselho correspondente.
        Em produção, essa lógica seria mais complexa.
        """
        # Aqui, a lógica real verificaria self.tipo_de_especialidade para saber qual conselho buscar.
        self.crp_cnr_cref_verificado = True # Corrected attribute name
        print(f"Profissional ({self.tipo_de_especialidade}) com registro {self.crp_cnr_cref} foi marcado para verificação.") # Corrected attribute name


    def definir_disponibilidade(self, dia, hora_inicio, hora_fim):
        """
        Cria um novo objeto AgendaProfissional para definir horários.
        """
        # Lógica para interagir com a classe AgendaProfissional
        print(f"Disponibilidade em {dia} das {hora_inicio} às {hora_fim} adicionada.")

# Exemplo de como criar um novo profissional:
# (Supondo que o id_usuario 5 já foi criado na tabela USUARIO)
# novo_nutricionista = Profissional(
#     id_profissional=5,
#     tipo_de_especialidade="Nutricionista", # Corrected parameter name
#     crp_cnr_cref="CRN-12345", # Corrected parameter name
#     valor_consulta=180.00
# )


class DadosBancarios(Base):
    __tablename__ = 'DADOS_BANCARIOS'

    # 1. Chaves
    id_bancario = Column(Integer, primary_key=True)
    # FK para Profissional (Relacionamento 1:1)
    # 'unique=True' garante que apenas um registro bancário exista por profissional.
    profissional_id = Column(Integer, ForeignKey('PROFISSIONAL.id_profissional'), unique=True, nullable=False)

    # 2. Dados Bancários
    banco = Column(String(50), nullable=False)
    agencia = Column(String(15), nullable=False)
    conta = Column(String(20), nullable=False)
    digito_verificador = Column(String(5))

    tipo_conta = Column(String(15), nullable=False) # Ex: Corrente, Poupança
    cpf_cnpj_titular = Column(String(20), nullable=False)
    nome_titular = Column(String(100), nullable=False)

    # -------------------------------------------------------------------------
    # Métodos de Lógica (Comportamento)
    # -------------------------------------------------------------------------

    def validar_dados(self):
        """
        Simula a validação dos dados bancários em um serviço de repasse financeiro.
        (Ex: Garantir que o CPF/CNPJ seja do titular da conta).
        """
        if len(self.cpf_cnpj_titular) < 11: # Checagem básica de CPF
            return False
        return True

    def processar_repasse(self, valor):
        """ Simula a transferência de fundos para a conta do profissional. """
        if self.validar_dados():
            print(f"Repasse de R$ {valor} processado para o Banco {self.banco}.")
            return True
        print("Erro: Dados bancários inválidos. Repasse falhou.")
        return False
      

class Pagamento(Base):
    __tablename__ = 'PAGAMENTO'

    # 1. Chaves
    # PK (ID de transação geralmente é uma string longa do gateway, mas INTEGER/VARCHAR serve)
    id_transacao = Column(String(50), primary_key=True)

    # FK para Agendamento (Um pagamento se refere a um agendamento)
    agendamento_id = Column(Integer, ForeignKey('AGENDAMENTO.id_agendamento'), unique=True, nullable=False)

    # FK opcional para Cupom (Um pagamento pode ou não usar um cupom)
    # cupom_id = Column(Integer, ForeignKey('CUPOM.id_cupom'), nullable=True)

    # 2. Dados Financeiros
    valor = Column(Numeric(10, 2), nullable=False)
    data_pagamento = Column(DateTime) # Data e hora que o pagamento foi aprovado

    # Definição das Opções para Status e Métodos de Pagamento
    # ----------------------------------------------------
    OPCOES_STATUS_PAGAMENTO = ["Pendente", "Aprovado", "Falhou", "Reembolsado"]
    OPCOES_METODO_PAGAMENTO = ["Cartao_Credito", "PIX", "Boleto"]

    # Status e Método (Usando Enum para garantir integridade)
    status = Column(Enum(*OPCOES_STATUS_PAGAMENTO, name='status_pag_options'), default="Pendente", nullable=False)
    metodo = Column(Enum(*OPCOES_METODO_PAGAMENTO, name='metodo_pag_options'), nullable=False)

    # -------------------------------------------------------------------------
    # Método Construtor (__init__)
    # -------------------------------------------------------------------------

    def __init__(self, agendamento_id, valor, metodo, cupom_id=None):
        # Gera um ID de transação fictício no momento da criação
        self.id_transacao = f"txn_{uuid.uuid4()}"
        self.agendamento_id = agendamento_id
        self.valor = valor
        self.metodo = metodo
        self.status = "Pendente"
        

class ContatoEmergencia(Base):
    __tablename__ = 'CONTATO_EMERGENCIA'

    # 1. Chave Primária
    id_contato = Column(Integer, primary_key=True)

    # FK: Relacionamento Muitos para Um (N:1) - Um paciente pode ter vários contatos
    paciente_id = Column(Integer, ForeignKey('PACIENTE.id_paciente'), nullable=False)

    # 2. Dados do Contato
    nome = Column(String(100), nullable=False)
    telefone = Column(String(20), nullable=False) # Armazenado como string
    relacionamento = Column(String(50)) # Ex: Mãe, Cônjuge, Amigo

    # 3. Relacionamento (Para acessar os dados do paciente)
    # paciente = relationship('Paciente', backref='contatos_emergencia')


    # -------------------------------------------------------------------------
    # Método Construtor (__init__)
    # -------------------------------------------------------------------------

    def __init__(self, paciente_id, nome, telefone, relacionamento):
        self.paciente_id = paciente_id
        self.nome = nome
        self.telefone = telefone
        self.relacionamento = relacionamento


    # -------------------------------------------------------------------------
    # Métodos de Lógica (Comportamento)
    # -------------------------------------------------------------------------

    def notificar_emergencia(self, mensagem=""):
        """
        Simula o envio de uma notificação ou SMS para o contato de emergência.
        """
        if not mensagem:
            mensagem = "URGENTE: Foi acionada uma emergência relacionada ao paciente."

        print("-----------------------------------------")
        print(f"ALERTA DE EMERGÊNCIA ENVIADO:")
        print(f"Destinatário: {self.nome} ({self.relacionamento})")
        print(f"Telefone: {self.telefone}")
        

class Agendamento(Base):
    __tablename__ = 'AGENDAMENTO'

    # 1. Chaves
    id_agendamento = Column(Integer, primary_key=True)

    # FKs: Relacionamento Muitos para Um (N:1)
    # Quem está atendendo
    profissional_id = Column(Integer, ForeignKey('PROFISSIONAL.id_profissional'), nullable=False)
    # Quem está sendo atendido
    paciente_id = Column(Integer, ForeignKey('PACIENTE.id_paciente'), nullable=False)

    # 2. Dados da Consulta

    # Data e Hora (usando tipos específicos do SQL)
    data_consulta = Column(Date, nullable=False)
    hora_consulta = Column(Time, nullable=False)
    # Definição das Opções para o Status do Agendamento
    # ----------------------------------------------------
    OPCOES_STATUS_AGENDAMENTO = ["Pendente", "Confirmado", "Concluido", "Cancelado"]
    # ----------------------------------------------------
    # Status e Link
    status = Column(Enum(*OPCOES_STATUS_AGENDAMENTO, name='status_agendamento_options'), default="Pendente", nullable=False)
    link_meet = Column(String(500)) # O link que será gerado

    # Atributo que confirma o recebimento do pagamento (libera a consulta)
    pagamento_confirmado = Column(Boolean, default=False)

    # 3. Relacionamentos

    # Relacionamento 1:1 com Pagamento (O pagamento que valida este agendamento)
    # O 'cascade' garante que se o agendamento for deletado, o pagamento associado também seja.
    pagamento = relationship('Pagamento', backref='agendamento', uselist=False, cascade="all, delete-orphan")

    # Relacionamentos de volta (backref) para Paciente e Profissional (assumindo que foram definidos nessas classes)

    # -------------------------------------------------------------------------
    # Método Construtor (__init__)
    # -------------------------------------------------------------------------

    def __init__(self, profissional_id, paciente_id, data_consulta, hora_consulta):
        self.profissional_id = profissional_id
        self.paciente_id = paciente_id
        self.data_consulta = data_consulta
        self.hora_consulta = hora_consulta
        self.link_meet = self._gerar_link_meet() # Gera o link ao criar o agendamento


    # -------------------------------------------------------------------------
    # Métodos de Lógica (Comportamento)
    # -------------------------------------------------------------------------

    def _gerar_link_meet(self):
        """
        Simula a geração de um link de reunião.
        Em um ambiente real, seria uma chamada a API do Google Calendar/Meet.
        """
        reuniao_id = ''.join(random.choices('abcdefghijkmnopqrstuvwxyz', k=10))
        return f"https://meet.google.com/{reuniao_id}"

    def liberar_consulta(self):
        """
        Método chamado após a aprovação do Pagamento.
        Confirma o agendamento e muda o status.
        """
        self.pagamento_confirmado = True
        self.status = "Confirmado"
        print(f"Agendamento {self.id_agendamento} LIBERADO e status alterado para {self.status}.")

    def registrar_conclusao(self):
        """
        Marca a consulta como concluída. Permite que o paciente faça a avaliação.
        """
        if self.status == "Confirmado":
            self.status = "Concluido"
            print(f"Agendamento {self.id_agendamento} marcado como CONCLUÍDO.")
            return True
        return False

# ----------------------------------------------------

class AgendaProfissional(Base):
    __tablename__ = 'AGENDA_PROFISSIONAL'

    # 1. Chaves
    id_disponibilidade = Column(Integer, primary_key=True)

    # FK: Relacionamento Muitos para Um (N:1) - Um profissional tem muitas entradas de agenda
    profissional_id = Column(Integer, ForeignKey('PROFISSIONAL.id_profissional'), nullable=False)

    # 2. Dados de Disponibilidade
    # Definição das Opções para o Dia da Semana

    OPCOES_DIA_SEMANA = [
    "Segunda",
    "Terça",
    "Quarta",
    "Quinta",
    "Sexta",
    "Sábado",
    "Domingo"]

    # Usando Enum para garantir consistência no nome dos dias
    dia_semana = Column(Enum(*OPCOES_DIA_SEMANA, name='dia_semana_options'), nullable=False)

    # Usando Time para armazenar apenas a hora
    hora_inicio = Column(Time, nullable=False)
    hora_fim = Column(Time, nullable=False)

    # Flag para indicar se o slot está ativo ou foi desativado temporariamente
    disponivel = Column(Boolean, default=True)

    # 3. Relacionamento (para acessar o profissional)
    # profissional = relationship('Profissional', backref='agenda')


    # -------------------------------------------------------------------------
    # Método Construtor (__init__)
    # -------------------------------------------------------------------------

    def __init__(self, profissional_id, dia_semana, hora_inicio, hora_fim):
        self.profissional_id = profissional_id
        self.dia_semana = dia_semana
        self.hora_inicio = hora_inicio
        self.hora_fim = hora_fim


    # -------------------------------------------------------------------------
    # Métodos de Lógica (Comportamento)
    # -------------------------------------------------------------------------

    def verificar_conflito(self, nova_hora_inicio, nova_hora_fim):
        """
        Verifica se um novo agendamento colide com este slot de disponibilidade.
        """
        # Comparação básica de horários. Requer conversão para objetos datetime.time()
        # Se a nova hora de início for ANTES do fim do slot E
        # a nova hora de fim for DEPOIS do início do slot, há conflito.
        if nova_hora_inicio < self.hora_fim and nova_hora_fim > self.hora_inicio:
            return True
        return False

    def desativar_slot(self):
        """ Marca este slot como indisponível (ex: feriado, compromisso). """
        self.disponivel = False
        print(f"Disponibilidade para {self.dia_semana} das {self.hora_inicio} foi desativada.")

# Exemplo de uso:
# agenda_segunda = AgendaProfissional(
#     profissional_id=1,
#     dia_semana="Segunda",
#     hora_inicio="09:00:00",
#     hora_fim="12:00:00"
# )


class Avaliacao(Base):
    __tablename__ = 'AVALIACAO' # Corrected typo

    # 1. Chaves
    id_avaliacao = Column(Integer, primary_key=True)

    # FKs: Relacionamento Muitos para Um (N:1)
    # Quem está avaliando
    paciente_id = Column(Integer, ForeignKey('PACIENTE.id_paciente'), nullable=False)
    # Quem está sendo avaliado
    profissional_id = Column(Integer, ForeignKey('PROFISSIONAL.id_profissional'), nullable=False)

    # FK Opcional: Se quiser garantir que a avaliação só possa ser feita após um agendamento
    agendamento_id = Column(Integer, ForeignKey('AGENDAMENTO.id_agendamento'), unique=True, nullable=True)

    # 2. Dados da Avaliação

    # Nota (usando SmallInteger para um número pequeno, ex: 1 a 5)
    nota = Column(SmallInteger, nullable=False)
    comentario = Column(Text)
    data_avaliacao = Column(DateTime, default=datetime.utcnow)

    # Definição das Opções de Status da Avaliação (para moderação)
    OPCOES_STATUS_AVALIACAO = ["Aprovada", "Pendente", "Denunciada"]

    # Status para moderação (garante que comentários ofensivos sejam revisados)
    status = Column(Enum(*OPCOES_STATUS_AVALIACAO, name='status_avaliacao_options'), default="Pendente", nullable=False)

    # -------------------------------------------------------------------------
    # Método Construtor (__init__)
    # -------------------------------------------------------------------------

    def __init__(self, paciente_id, profissional_id, nota, comentario=None, agendamento_id=None):
        self.paciente_id = paciente_id # Added self.
        self.profissional_id = profissional_id # Added self.
        self.nota = nota # Added self.
        self.comentario = comentario # Added self.
        self.agendamento_id = agendamento_id # Added self.

    # -------------------------------------------------------------------------
    # Métodos de Lógica (Comportamento)
    # -------------------------------------------------------------------------

    def denunciar_avaliacao(self):
        """ Marca a avaliação como denunciada para revisão. """
        self.status = "Denunciada"
        print(f"Avaliação {self.id_avaliacao} marcada como DENUNCIADA.")

    def aprovar_avaliacao(self):
        """ Marca a avaliação como aprovada (após revisão). """
        self.status = "Aprovada"
        print(f"Avaliação {self.id_avaliacao} marcada como APROVADA.")

    def calcular_media_profissional(self, profissional_id):
        """
        Calcula a média das notas de avaliação para um profissional específico.
        Em um aplicativo real, essa seria uma consulta ao banco de dados.
        """
        # Simulação: Buscar todas as avaliações do profissional e calcular a média
        # from sqlalchemy import func
        # media = session.query(func.avg(Avaliacao.nota)).filter_by(profissional_id=profissional_id).scalar()
        # return media if media is not None else 0

        print(f"Simulando cálculo da média de avaliações para o Profissional ID {profissional_id}.")
        return 4.5 # Exemplo de retorno simulado
      
      
class Notificacao(Base):
    __tablename__ = 'NOTIFICACAO'

    # 1. Chaves
    id_notificacao = Column(Integer, primary_key=True)

    # FK: O usuário que deve receber (pode ser Paciente ou Profissional)
    usuario_id = Column(Integer, ForeignKey('USUARIO.id_usuario'), nullable=False)

    # FK Opcional para associar a uma transação (Agendamento, Pagamento, etc.)
    agendamento_id = Column(Integer, ForeignKey('AGENDAMENTO.id_agendamento'), nullable=True)

    # 2. Dados da Notificação

    # Definição dos Tipos de Notificação

    OPCOES_TIPO_NOTIFICACAO = ["Lembrete Consulta", "Pagamento Status", "Alerta Sistema", "Feedback Avaliacao"]
    # Tipo (limitado por Enum)
    tipo_notificacao = Column(Enum(*OPCOES_TIPO_NOTIFICACAO, name='tipo_notificacao_options'), nullable=False)

    mensagem = Column(Text, nullable=False)
    data_envio = Column(DateTime, default=datetime.utcnow)

    # Status de leitura
    lida = Column(Boolean, default=False)


    # -------------------------------------------------------------------------
    # Método Construtor (__init__)
    # -------------------------------------------------------------------------

    def __init__(self, usuario_id, tipo_notificacao, mensagem, agendamento_id=None):
        self.usuario_id = usuario_id
        self.tipo_notificacao = tipo_notificacao
        self.mensagem = mensagem
        self.agendamento_id = agendamento_id


    # -------------------------------------------------------------------------
    # Métodos de Lógica (Comportamento)
    # -------------------------------------------------------------------------

    def enviar_notificacao(self):
        """
        Simula o envio real da notificação (SMS, E-mail ou Push Notification).
        """
        # Aqui, a lógica real de envio seria implementada.
        print(f"--- Envio de Notificação ---")
        print(f"Para Usuário ID {self.usuario_id} | Tipo: {self.tipo_notificacao}")
        print(f"Conteúdo: {self.mensagem[:50]}...")

    def marcar_como_lida(self):
        """ Atualiza o status de leitura no banco de dados. """
        self.lida = True
        print(f"Notificação {self.id_notificacao} marcada como lida.")
        


Base.metadata.create_all(engine)
#criação do banco de dados e das tabelas

