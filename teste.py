import os
from datetime import datetime, date, time
from sqlalchemy.orm import sessionmaker

# Importar tudo o que for necessário do arquivo de modelos
from Model import (
    engine, Base, DB_FILE,
    Usuario, Endereco, Paciente, Profissional, DadosBancarios,
    Pagamento, ContatoEmergencia, Agendamento, AgendaProfissional,
    Avaliacao, Notificacao
)

# --- Preparação do Ambiente de Teste ---



# 2. Recriar todas as tabelas
Base.metadata.create_all(engine)
print("Novas tabelas criadas.")

# 3. Configurar a Sessão
Session = sessionmaker(bind=engine)
session = Session()

# ======================================================================
# =================== INÍCIO DO SCRIPT DE TESTE ========================
# ======================================================================

print("\n--- Iniciando Teste do Sistema TCC ---")

try:
    # 2. Criar Usuários (Paciente e Profissional)
    print("\n[1. Criando Usuários]")
    usuario_paciente = Usuario(
        nome="Ana Silva",
        email="ana.silva@email.com",
        senha="senha123",
        termos_aceitos=True,
        data_de_nascimento=date(1990, 5, 15),
        RG="1234567-8",
        CPF="111.222.333-44",
        genero="Feminino Cis",
        telefone="11987654321"
    )
    
    usuario_profissional = Usuario(
        nome="Dr. Bruno Costa",
        email="bruno.costa@email.com",
        senha="senha456",
        termos_aceitos=True,
        data_de_nascimento=date(1985, 10, 20),
        RG="9876543-2",
        CPF="444.555.666-77",
        genero="Masculino Cis",
        telefone="11912345678"
    )
    session.add_all([usuario_paciente, usuario_profissional])
    session.commit() # Commit para gerar os IDs
    
    print(f"Paciente criado: {usuario_paciente.nome} (ID: {usuario_paciente.id_usuario})")
    print(f"Profissional criado: {usuario_profissional.nome} (ID: {usuario_profissional.id_usuario})")

    # 3. Criar Perfis (Paciente e Profissional)
    print("\n[2. Criando Perfis]")
    paciente = Paciente(id_paciente=usuario_paciente.id_usuario)
    paciente.historico_medico = "Paciente relata ansiedade e busca acompanhamento."
    
    profissional = Profissional(
        id_profissional=usuario_profissional.id_usuario,
        tipo_de_especialidade="Psicólogo",
        crp_cnr_cref="CRP-06/123456",
        valor_consulta=250.00
    )
    session.add_all([paciente, profissional])
    session.commit()
    
    # Testando o acesso ao relacionamento (Profissional -> Usuario.nome)
    print(f"Perfil Paciente para '{paciente.usuario.nome}' criado.")
    print(f"Perfil Profissional para '{profissional.usuario.nome}' criado.")

    # 4. Adicionar Detalhes e Relações
    print("\n[3. Adicionando Detalhes (Endereços, Banco, Contato, Agenda)]")
    
    # Endereço Paciente
    end_paciente = Endereco(
        cep="01000-000", logradouro="Rua A", numero="10",
        bairro="Centro", cidade="São Paulo", estado="SP"
    )
    session.add(end_paciente)
    session.commit() # Commit para gerar ID do endereço
    paciente.endereco_id = end_paciente.id_endereco # Associando o endereço ao paciente
    
    # Dados Bancários do Profissional (usa relacionamento 1:1)
    dados_bancarios = DadosBancarios(
        profissional_id=profissional.id_profissional,
        banco="Banco XYZ", agencia="0001", conta="12345-6",
        tipo_conta="Corrente", cpf_cnpj_titular=profissional.usuario.CPF,
        nome_titular=profissional.usuario.nome
    )
    session.add(dados_bancarios)
    
    # Contato de Emergência do Paciente
    contato_emerg = ContatoEmergencia(
        paciente_id=paciente.id_paciente,
        nome="Carlos Silva",
        telefone="11999998888",
        relacionamento="Irmão"
    )
    session.add(contato_emerg)
    
    # Agenda do Profissional
    agenda_prof = AgendaProfissional(
        profissional_id=profissional.id_profissional,
        dia_semana="Quarta",
        hora_inicio=time(14, 0, 0),
        hora_fim=time(18, 0, 0)
    )
    session.add(agenda_prof)
    
    session.commit()
    print("Endereços, Dados Bancários, Contato de Emergência e Agenda criados.")

    # 5. Simulação: Agendamento e Pagamento
    print("\n[4. Simulação de Agendamento e Pagamento]")
    
    # Paciente agenda consulta
    novo_agendamento = Agendamento(
        profissional_id=profissional.id_profissional,
        paciente_id=paciente.id_paciente,
        data_consulta=date(2025, 10, 22), # Uma quarta-feira
        hora_consulta=time(15, 0, 0)     # Dentro da disponibilidade (14h-18h)
    )
    session.add(novo_agendamento)
    session.commit()
    print(f"Agendamento criado (ID: {novo_agendamento.id_agendamento}). Status: {novo_agendamento.status}")
    print(f"Link da consulta gerado: {novo_agendamento.link_meet}")
    
    # Sistema cria o pagamento
    pagamento = Pagamento(
        agendamento_id=novo_agendamento.id_agendamento,
        valor=profissional.valor_consulta,
        metodo="PIX"
    )
    session.add(pagamento)
    session.commit()
    print(f"Pagamento gerado (ID: {pagamento.id_transacao}). Status: {pagamento.status}")
    
    # Simula aprovação do pagamento (ex: webhook do gateway)
    pagamento.status = "Aprovado"
    pagamento.data_pagamento = datetime.utcnow()
    session.commit()
    print(f"Pagamento {pagamento.id_transacao} APROVADO.")
    
    # Libera a consulta (chamando o método da classe Agendamento)
    novo_agendamento.liberar_consulta()
    session.commit()
    print(f"Status do agendamento {novo_agendamento.id_agendamento} atualizado para: {novo_agendamento.status}")

    # 6. Simulação: Pós-Consulta (Conclusão e Avaliação)
    print("\n[5. Simulação Pós-Consulta]")
    
    # Profissional marca como concluída
    novo_agendamento.registrar_conclusao()
    session.commit()
    print(f"Status do agendamento {novo_agendamento.id_agendamento} atualizado para: {novo_agendamento.status}")
    
    # Paciente faz a avaliação
    avaliacao = Avaliacao(
        paciente_id=paciente.id_paciente,
        profissional_id=profissional.id_profissional,
        agendamento_id=novo_agendamento.id_agendamento,
        nota=5,
        comentario="Excelente profissional, muito atencioso."
    )
    session.add(avaliacao)
    session.commit()
    print(f"Avaliação (ID: {avaliacao.id_avaliacao}) criada. Status: {avaliacao.status}")
    
    # Admin aprova a avaliação (chamando o método)
    avaliacao.aprovar_avaliacao()
    session.commit()

    # 7. Simulação: Notificações
    print("\n[6. Simulação de Notificações]")
    
    # Notificação para o Paciente
    notif_paciente = Notificacao(
        usuario_id=paciente.usuario.id_usuario,
        tipo_notificacao="Lembrete Consulta",
        mensagem=f"Lembrete: Sua consulta com {profissional.usuario.nome} é amanhã às {novo_agendamento.hora_consulta}."
    )
    
    # Notificação para o Profissional
    notif_profissional = Notificacao(
        usuario_id=profissional.usuario.id_usuario,
        tipo_notificacao="Feedback Avaliacao",
        mensagem=f"Você recebeu uma nova avaliação de 5 estrelas de {paciente.usuario.nome}."
    )
    
    session.add_all([notif_paciente, notif_profissional])
    session.commit()
    
    # Simula o "envio" (chamando os métodos)
    notif_paciente.enviar_notificacao()
    notif_profissional.enviar_notificacao()
    
    # 8. Verificação Final (Consultas ao Banco)
    print("\n[7. Verificação Final no Banco (Queries)]")
    
    # Consultar o profissional e seus detalhes (testando relacionamento 1:1)
    prof_consulta = session.query(Profissional).filter_by(id_profissional=usuario_profissional.id_usuario).one()
    
    print(f"Profissional: {prof_consulta.usuario.nome}")
    print(f"Especialidade: {prof_consulta.tipo_de_especialidade}")
    print(f"Banco (via relationship): {prof_consulta.dados_bancarios.banco} - {prof_consulta.dados_bancarios.agencia}/{prof_consulta.dados_bancarios.conta}")
    
    # Consultar o paciente e seus detalhes (testando FK)
    pac_consulta = session.query(Paciente).filter_by(id_paciente=usuario_paciente.id_usuario).one()
    # Buscar o endereço separado, pois o relationship não foi definido (o que está OK)
    endereco_pac = session.query(Endereco).filter_by(id_endereco=pac_consulta.endereco_id).one()
    
    print(f"Paciente: {pac_consulta.usuario.nome}")
    print(f"Endereço (via método .formatar_endereco()): {endereco_pac.formatar_endereco()}")

    # Contar agendamentos concluídos
    agendamentos_concluidos = session.query(Agendamento).filter_by(status="Concluido").count()
    print(f"Total de agendamentos concluídos no sistema: {agendamentos_concluidos}")
    
    print("\n--- Teste Concluído com Sucesso ---")

except Exception as e:
    print(f"\n--- OCORREU UM ERRO DURANTE O TESTE ---")
    print(e)
    session.rollback() # Desfazer alterações em caso de erro
    
finally:
    session.close()
    print("Sessão do banco de dados fechada.")