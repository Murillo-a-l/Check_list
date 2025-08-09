import flet as ft
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
import json
import os
import shutil
from datetime import datetime
import subprocess
import platform
import re
import base64
import unittest
from unittest.mock import Mock, patch, MagicMock
import logging
from logging.handlers import RotatingFileHandler

# =================== CONFIGURAÇÃO E CONSTANTES ===================

class ConfigSistema:
    """Configurações centralizadas do sistema"""
    
    # Cores da marca LaborePlus
    AZUL_MARCA = "#00365f"
    BEGE_MARCA = "#d4a574"
    VERDE_MODERNO = "#10b981"
    CINZA_ESCURO = "#374151"
    CINZA_CLARO = "#f3f4f6"
    BRANCO = "#ffffff"
    VERMELHO = "#ef4444"
    
    # Configurações da aplicação
    WINDOW_TITLE = "Sistema de Checklist Clínico - LaborePlus"
    WINDOW_BGCOLOR = "#f8fafc"
    
    # Procedimentos padrão
    PROCEDIMENTOS_PADRAO = [
        "Exame Clínico", "Faturamento", "Audiometria", "Espirometria",
        "Eletrocardiograma", "Hemograma Completo", "Glicemia",
        "Exame de Urina", "Raio-X Tórax", "Acuidade Visual", "Exame Dermatológico"
    ]

# =================== VALIDAÇÕES AVANÇADAS ===================

class ValidadorAvancado:
    """Validações avançadas para o sistema"""
    
    @staticmethod
    def validar_nome_completo(nome):
        """Valida se o nome está completo"""
        if not nome or len(nome.strip()) < 3:
            return False, "Nome deve ter pelo menos 3 caracteres"
        
        palavras = nome.strip().split()
        if len(palavras) < 2:
            return False, "Digite o nome completo (nome e sobrenome)"
        
        # Verificar se não tem números
        if any(char.isdigit() for char in nome):
            return False, "Nome não pode conter números"
        
        return True, ""
    
    @staticmethod
    def validar_procedimentos_minimos(procedimentos, obrigatorios):
        """Valida se tem procedimentos mínimos"""
        if not procedimentos:
            return False, "Selecione pelo menos um procedimento"
        
        faltantes = [proc for proc in obrigatorios if proc not in procedimentos]
        if faltantes:
            return False, f"Procedimentos obrigatórios faltantes: {', '.join(faltantes)}"
        
        return True, ""
    
    @staticmethod
    def validar_compatibilidade_tipo_procedimentos(tipo_exame, procedimentos):
        """Valida se os procedimentos são compatíveis com o tipo de exame"""
        # Regras específicas por tipo
        restricoes = {
            'demissional': {
                'proibidos': ['Raio-X Tórax', 'Espirometria'],
                'motivo': 'não são necessários para exame demissional'
            }
        }
        
        tipo_lower = tipo_exame.lower()
        if tipo_lower in restricoes:
            restricao = restricoes[tipo_lower]
            proibidos_encontrados = [p for p in procedimentos if p in restricao['proibidos']]
            
            if proibidos_encontrados:
                return False, f"Procedimentos {', '.join(proibidos_encontrados)} {restricao['motivo']}"
        
        return True, ""

# =================== SISTEMA DE LOGS AVANÇADO ===================

class GerenciadorLogs:
    """Sistema avançado de logs com rotação"""
    
    def __init__(self):
        self._configurar_logs()
    
    def _configurar_logs(self):
        """Configura sistema de logs com rotação"""
        # Criar logger principal
        self.logger = logging.getLogger('SistemaClinico')
        self.logger.setLevel(logging.INFO)
        
        # Evitar duplicação se já configurado
        if self.logger.handlers:
            return
        
        # Handler para arquivo com rotação
        file_handler = RotatingFileHandler(
            'sistema_clinico.log',
            maxBytes=5*1024*1024,  # 5MB
            backupCount=5,
            encoding='utf-8'
        )
        file_handler.setLevel(logging.INFO)
        
        # Handler para console
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.WARNING)
        
        # Formato das mensagens
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        # Adicionar handlers
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
    
    def log_geracao_pdf(self, nome, cpf, tipo_exame, procedimentos, filename):
        """Log específico para geração de PDF"""
        self.logger.info(
            f"PDF gerado - Nome: {nome}, CPF: {cpf[:3]}.***.***-**, "
            f"Tipo: {tipo_exame}, Procedimentos: {len(procedimentos)}, Arquivo: {filename}"
        )
    
    def log_erro(self, operacao, erro):
        """Log de erro com contexto"""
        self.logger.error(f"Erro em {operacao}: {str(erro)}")
    
    def log_acao_usuario(self, acao, detalhes=""):
        """Log de ações do usuário"""
        self.logger.info(f"Ação: {acao} - {detalhes}")
    
    def log_historico(self, acao, funcionario="", detalhes=""):
        """Log específico para histórico"""
        self.logger.info(f"Histórico - {acao}: {funcionario} - {detalhes}")
        
    def salvar_historico(self):
        """Método de compatibilidade - apenas log"""
        self.logger.info("Tentativa de salvar histórico via GerenciadorLogs")
        return True
        
# =================== GERENCIADOR DE HISTÓRICO ===================

class GerenciadorHistorico:
    """Gerencia histórico de checklists com funcionalidades de busca e edição"""
    
    def __init__(self):
        self.arquivo_historico = 'historico_checklists.json'
        self.historico = self.carregar_historico()
    
    def carregar_historico(self):
        """Carrega histórico do arquivo JSON"""
        if os.path.exists(self.arquivo_historico):
            try:
                with open(self.arquivo_historico, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return []
        return []
    
    def salvar_historico(self):
        """Salva histórico no arquivo JSON"""
        try:
            with open(self.arquivo_historico, 'w', encoding='utf-8') as f:
                json.dump(self.historico, f, ensure_ascii=False, indent=2)
            return True
        except:
            return False
    
    def adicionar_checklist(self, nome, cpf, tipo_exame, procedimentos, arquivo_pdf):
        """Adiciona novo checklist ao histórico"""
        novo_registro = {
            'id': len(self.historico) + 1,
            'timestamp': datetime.now().isoformat(),
            'data_formatada': datetime.now().strftime('%d/%m/%Y %H:%M'),
            'nome': nome.strip(),
            'cpf': cpf,
            'tipo_exame': tipo_exame,
            'procedimentos': procedimentos.copy(),
            'arquivo_pdf': arquivo_pdf,
            'editado': False,
            'historico_edicoes': []
        }
        
        self.historico.append(novo_registro)
        self.salvar_historico()
        return novo_registro['id']
    
    def buscar_por_funcionario(self, nome_parcial):
        """Busca checklists por nome (busca parcial)"""
        nome_limpo = nome_parcial.strip().lower()
        resultados = [r for r in self.historico if nome_limpo in r['nome'].lower()]
        return sorted(resultados, key=lambda x: x['timestamp'], reverse=True)
    
    def buscar_por_cpf(self, cpf):
        """Busca checklists por CPF"""
        cpf_limpo = cpf.replace('.', '').replace('-', '').strip()
        resultados = []
        
        for registro in self.historico:
            registro_cpf = registro['cpf'].replace('.', '').replace('-', '').strip()
            if cpf_limpo == registro_cpf:
                resultados.append(registro)
        
        return sorted(resultados, key=lambda x: x['timestamp'], reverse=True)
    
    def obter_funcionarios_unicos(self):
        """Obtém lista única de funcionários com dados mais recentes"""
        funcionarios = {}
        
        for registro in self.historico:
            nome = registro['nome']
            if nome not in funcionarios or registro['timestamp'] > funcionarios[nome]['timestamp']:
                funcionarios[nome] = {
                    'nome': registro['nome'],
                    'cpf': registro['cpf'],
                    'ultimo_tipo_exame': registro['tipo_exame'],
                    'ultima_data': registro['data_formatada'],
                    'total_checklists': 0,
                    'timestamp': registro['timestamp']
                }
        
        # Contar total de checklists por funcionário
        for registro in self.historico:
            nome = registro['nome']
            if nome in funcionarios:
                funcionarios[nome]['total_checklists'] += 1
        
        return list(funcionarios.values())

# =================== CLASSES PRINCIPAIS ===================

class SistemaClinico:
    """Classe principal para gerenciamento de dados clínicos"""
    
    def __init__(self):
        self.procedimentos_db = []
        self.funcionarios_db = []
        self.historico = []
        self.logo_path = None
        self.logo_pdf_path = None
        self.procedimentos_obrigatorios = ["Exame Clínico", "Faturamento", "Triagem"]
        self.carregar_dados()
        
        # FORÇAR atualização dos procedimentos obrigatórios
        self._garantir_procedimentos_obrigatorios_completos()
        
    def carregar_dados(self):
        """Carrega procedimentos e configurações salvos"""
        if os.path.exists('procedimentos.json'):
            with open('procedimentos.json', 'r', encoding='utf-8') as f:
                dados = json.load(f)
                # Compatibilidade com versão antiga (lista simples)
                if isinstance(dados, list):
                    self.procedimentos_db = {}
                    for proc in dados:
                        self.procedimentos_db[proc] = {"requer_laudo": False}
                else:
                    self.procedimentos_db = dados
        else:
            # Inicializar com estrutura nova (dicionário)
            procedimentos_iniciais = [
                "Exame Clínico", "Faturamento", "Triagem", "Audiometria", "Espirometria",
                "Eletrocardiograma", "Hemograma Completo", "Glicemia",
                "Exame de Urina", "Raio-X Tórax", "Acuidade Visual", "Exame Dermatológico"
            ]
            self.procedimentos_db = {}
            for proc in procedimentos_iniciais:
                self.procedimentos_db[proc] = {"requer_laudo": False}
            self.salvar_procedimentos()
        
        if os.path.exists('config.json'):
            with open('config.json', 'r', encoding='utf-8') as f:
                config = json.load(f)
                self.logo_path = config.get('logo_path')
                self.logo_pdf_path = config.get('logo_pdf_path')
                self.procedimentos_obrigatorios = config.get('procedimentos_obrigatorios', ["Exame Clínico", "Faturamento", "Triagem"])
                
    def _garantir_procedimentos_obrigatorios_completos(self):
        """Garante que todos os procedimentos obrigatórios estejam configurados"""
        obrigatorios_padrao = ["Exame Clínico", "Faturamento", "Triagem"]
        
        # Garantir que todos estejam na lista de obrigatórios
        for obrig in obrigatorios_padrao:
            if obrig not in self.procedimentos_obrigatorios:
                self.procedimentos_obrigatorios.append(obrig)
        
        # Garantir que todos existam no banco de procedimentos
        for obrig in obrigatorios_padrao:
            if obrig not in self.procedimentos_db:
                self.procedimentos_db[obrig] = {"requer_laudo": False}
        
        # Salvar as alterações
        self.salvar_procedimentos()
        self.salvar_config()
    
    @property
    def lista_procedimentos(self):
        """Retorna lista de nomes dos procedimentos"""
        return list(self.procedimentos_db.keys())

    def procedimento_requer_laudo(self, procedimento):
        """Verifica se procedimento requer laudo"""
        return self.procedimentos_db.get(procedimento, {}).get("requer_laudo", False)

    def definir_requer_laudo(self, procedimento, requer):
        """Define se procedimento requer laudo"""
        if procedimento in self.procedimentos_db:
            self.procedimentos_db[procedimento]["requer_laudo"] = requer
            self.salvar_procedimentos()
            return True
        return False
    
    def salvar_procedimentos(self):
        """Salva lista de procedimentos no arquivo JSON"""
        try:
            with open('procedimentos.json', 'w', encoding='utf-8') as f:
                json.dump(self.procedimentos_db, f, ensure_ascii=False, indent=2)
            return True
        except (IOError, UnicodeError) as e:
            print(f"Erro ao salvar procedimentos: {e}")
            return False

    def salvar_config(self):
        """Salva configurações no arquivo JSON"""
        try:
            config = {
                'logo_path': self.logo_path,
                'logo_pdf_path': self.logo_pdf_path,
                'procedimentos_obrigatorios': self.procedimentos_obrigatorios
            }
            with open('config.json', 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
            return True
        except (IOError, UnicodeError) as e:
            print(f"Erro ao salvar configurações: {e}")
            return False
    
    def adicionar_procedimento(self, procedimento):
        """Adiciona novo procedimento se não existir"""
        if procedimento and procedimento not in self.procedimentos_db:
            self.procedimentos_db[procedimento] = {"requer_laudo": False}
            self.salvar_procedimentos()
            return True
        return False
    
    def remover_procedimento_db(self, procedimento):
        """Remove procedimento da base de dados"""
        if procedimento in self.procedimentos_db:
            del self.procedimentos_db[procedimento]
            self.salvar_procedimentos()
            return True
        return False
    
    def alternar_obrigatorio(self, procedimento):
        """Alterna status obrigatório de um procedimento"""
        if procedimento in self.procedimentos_obrigatorios:
            self.procedimentos_obrigatorios.remove(procedimento)
        else:
            self.procedimentos_obrigatorios.append(procedimento)
        self.salvar_config()
        return True
    
    def editar_procedimento_db(self, procedimento_antigo, procedimento_novo):
        """Edita nome de um procedimento existente"""
        if procedimento_antigo in self.procedimentos_db and procedimento_novo:
            # Copiar dados do procedimento antigo
            dados_antigos = self.procedimentos_db[procedimento_antigo]
            
            # Remover antigo e adicionar novo
            del self.procedimentos_db[procedimento_antigo]
            self.procedimentos_db[procedimento_novo] = dados_antigos
            
            # Atualizar lista de obrigatórios
            if procedimento_antigo in self.procedimentos_obrigatorios:
                obrig_index = self.procedimentos_obrigatorios.index(procedimento_antigo)
                self.procedimentos_obrigatorios[obrig_index] = procedimento_novo
            
            self.salvar_procedimentos()
            self.salvar_config()
            return True
        return False
    
    def validar_cpf(self, cpf):
        """Valida CPF usando algoritmo oficial"""
        cpf = re.sub(r'[^0-9]', '', cpf)
        
        if len(cpf) != 11 or cpf == cpf[0] * 11:
            return False
        
        # Validação primeiro dígito
        soma = sum(int(cpf[i]) * (10 - i) for i in range(9))
        resto = 11 - (soma % 11)
        if resto == 10 or resto == 11:
            resto = 0
        if resto != int(cpf[9]):
            return False
        
        # Validação segundo dígito
        soma = sum(int(cpf[i]) * (11 - i) for i in range(10))
        resto = 11 - (soma % 11)
        if resto == 10 or resto == 11:
            resto = 0
        if resto != int(cpf[10]):
            return False
        
        return True
    
    def formatar_cpf(self, cpf):
        """Aplica máscara no CPF"""
        cpf = re.sub(r'[^0-9]', '', cpf)
        
        if len(cpf) <= 3:
            return cpf
        elif len(cpf) <= 6:
            return f"{cpf[:3]}.{cpf[3:]}"
        elif len(cpf) <= 9:
            return f"{cpf[:3]}.{cpf[3:6]}.{cpf[6:]}"
        elif len(cpf) <= 11:
            return f"{cpf[:3]}.{cpf[3:6]}.{cpf[6:9]}-{cpf[9:]}"
        else:
            return f"{cpf[:3]}.{cpf[3:6]}.{cpf[6:9]}-{cpf[9:11]}"
    
    def gerar_pdf_checklist(self, nome, cpf, tipo_exame, procedimentos_selecionados):
        """Gera PDF do checklist"""
        filename = f"checklist_{nome.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        
        c = canvas.Canvas(filename, pagesize=A4)
        width, height = A4
        
        # Cabeçalho
        c.setFillColorRGB(1, 1, 1)
        c.setStrokeColorRGB(0, 0.212, 0.373)
        c.setLineWidth(2)
        
        rect_x, rect_y, rect_width, rect_height, radius = 30, height - 100, width - 60, 90, 10
        c.roundRect(rect_x, rect_y, rect_width, rect_height, radius, fill=1, stroke=1)
        
        # Título
        c.setFillColorRGB(0, 0.212, 0.373)
        c.setFont("Helvetica-Bold", 22)
        text_width = c.stringWidth("CHECKLIST", "Helvetica-Bold", 22)
        center_x = (width - text_width) / 2
        center_y = rect_y + (rect_height / 2) - 6
        c.drawString(center_x, center_y, "CHECKLIST")
        
        # Logo
        if self.logo_pdf_path and os.path.exists(self.logo_pdf_path):
            try:
                from reportlab.lib.utils import ImageReader
                logo = ImageReader(self.logo_pdf_path)
                c.drawImage(logo, width - 180, height - 95, width=140, height=80, mask='auto')
            except:
                self._desenhar_logo_placeholder(c, width, height)
        else:
            self._desenhar_logo_placeholder(c, width, height)
        
        # Informações do funcionário
        c.setFillColorRGB(0, 0, 0)
        c.setFont("Helvetica-Bold", 14)
        c.drawString(50, height - 130, f"Funcionário: {nome}")
        c.drawString(50, height - 150, f"CPF: {cpf}")
        c.drawString(50, height - 170, f"Tipo de Exame: {tipo_exame}")
        c.drawString(50, height - 190, f"Data: {datetime.now().strftime('%d/%m/%Y')}")
        
        # Linha separadora
        c.setStrokeColorRGB(0.894, 0.780, 0.690)
        c.setLineWidth(2)
        c.line(50, height - 210, width - 50, height - 210)
        
        # Verificar se tem Triagem para desenhar o card
        tem_triagem = "Triagem" in procedimentos_selecionados
        if tem_triagem:
            self._desenhar_card_triagem(c, width, height)

        # Procedimentos
        c.setFillColorRGB(0, 0.212, 0.373)
        c.setFont("Helvetica-Bold", 16)
        c.drawString(50, height - 240, "PROCEDIMENTOS:")
        
        y_position = height - 270
        c.setFillColorRGB(0, 0, 0)
        c.setFont("Helvetica", 12)
        
        # CALCULAR TAMANHOS DE FONTE DINAMICAMENTE
        def calcular_espaco_necessario():
            """Calcula espaço necessário para todos os procedimentos"""
            espaco_total = 0
            for proc in procedimentos_selecionados:
                espaco_total += 25  # Espaço principal do procedimento
                if self.procedimento_requer_laudo(proc):
                    espaco_total += 20  # Espaço do sub-item
                espaco_total += 10  # Espaço extra entre procedimentos
            return espaco_total

        # Espaço disponível para procedimentos (da linha bege até o rodapé)
        y_inicio = height - 270  # Início dos procedimentos
        y_final = 80  # Espaço para rodapé
        espaco_disponivel = y_inicio - y_final

        # Calcular espaço necessário
        espaco_necessario = calcular_espaco_necessario()

        # Calcular fator de escala se não couber
        if espaco_necessario > espaco_disponivel:
            fator_escala = espaco_disponivel / espaco_necessario
            fonte_numero = max(10, int(14 * fator_escala))  # Mínimo 10pt
            fonte_procedimento = max(9, int(12 * fator_escala))  # Mínimo 9pt
            fonte_subitem = max(8, int(10 * fator_escala))  # Mínimo 8pt
            espaco_procedimento = max(18, int(25 * fator_escala))
            espaco_subitem = max(15, int(20 * fator_escala))
            espaco_extra = max(5, int(10 * fator_escala))
            tamanho_checkbox = max(12, int(15 * fator_escala))
            tamanho_subcheckbox = max(10, int(12 * fator_escala))
        else:
            # Tamanhos normais
            fonte_numero = 14
            fonte_procedimento = 12
            fonte_subitem = 10
            espaco_procedimento = 25
            espaco_subitem = 20
            espaco_extra = 10
            tamanho_checkbox = 15
            tamanho_subcheckbox = 12

        # DESENHAR PROCEDIMENTOS COM FONTES AJUSTADAS
        for i, procedimento in enumerate(procedimentos_selecionados, 1):
            # Posições
            numero_x = 50
            checkbox_x = 85
            texto_x = checkbox_x + 25
            baseline_y = y_position
            
            # Número em negrito
            c.setFillColorRGB(0, 0.212, 0.373)
            c.setFont("Helvetica-Bold", fonte_numero)
            c.drawString(numero_x, baseline_y, f"{i}.")
            
            # Checkbox do procedimento
            c.setStrokeColorRGB(0, 0.212, 0.373)
            c.setLineWidth(1.5)
            checkbox_y_centralizado = baseline_y + (fonte_numero/2) - (tamanho_checkbox/2)
            c.rect(checkbox_x, checkbox_y_centralizado, tamanho_checkbox, tamanho_checkbox)
            
            # Nome do procedimento
            c.setFillColorRGB(0, 0, 0)
            c.setFont("Helvetica-Bold", fonte_procedimento)
            c.drawString(texto_x, baseline_y, procedimento)
            
            y_position -= espaco_procedimento
            
            # Sub-item se precisa de laudo
            if self.procedimento_requer_laudo(procedimento):
                sub_baseline_y = y_position
                sub_checkbox_x = texto_x + 10
                
                # Checkbox do sub-item
                c.setStrokeColorRGB(0.5, 0.5, 0.5)
                c.setLineWidth(1)
                sub_checkbox_y_centralizado = sub_baseline_y + (fonte_subitem/2) - (tamanho_subcheckbox/2)
                c.rect(sub_checkbox_x, sub_checkbox_y_centralizado, tamanho_subcheckbox, tamanho_subcheckbox)
                
                # Texto do sub-item
                c.setFillColorRGB(0, 0, 0)
                c.setFont("Helvetica-Bold", fonte_subitem)
                c.drawString(sub_checkbox_x + 20, sub_baseline_y, "Impresso/Laudo realizado")
                
                y_position -= espaco_subitem
            
            y_position -= espaco_extra
        
        # Rodapé
        c.setFillColorRGB(0.5, 0.5, 0.5)
        c.setFont("Helvetica", 10)
        texto_rodape = "Sistema Checklist LaborePlus - Todos os direitos reservados"
        texto_width = c.stringWidth(texto_rodape, "Helvetica", 10)
        texto_x = (width - texto_width) / 2  # Centralizar horizontalmente
        c.drawString(texto_x, 50, texto_rodape)
        
        c.save()
        return filename
    
    def _desenhar_logo_placeholder(self, c, width, height):
        """Desenha logo placeholder no PDF"""
        c.setFillColorRGB(0.894, 0.780, 0.690)
        c.circle(width - 100, height - 55, 35, fill=1)
        c.setFillColorRGB(0, 0.212, 0.373)
        c.setFont("Helvetica-Bold", 14)
        c.drawString(width - 125, height - 60, "LOGO")
        
    def _desenhar_card_triagem(self, c, width, height):
        """Desenha card moderno de triagem no lado direito do PDF"""
        # Dimensões do card
        card_width = 180
        card_height = 150
        
        # ALINHAR: borda direita do card com final da linha bege (width - 50)
        linha_bege_final_x = width - 50
        card_x = linha_bege_final_x - card_width  # Borda direita = final da linha bege
        
        # Posição vertical (original)
        card_y = height - 380
        
        # Fundo do card com sombra
        c.setFillColorRGB(0.95, 0.95, 0.95)  # Sombra
        c.roundRect(card_x + 3, card_y - 3, card_width, card_height, 10, fill=1, stroke=0)
        
        # Card principal
        c.setFillColorRGB(1, 1, 1)  # Fundo branco
        c.setStrokeColorRGB(0, 0.212, 0.373)  # Borda azul
        c.setLineWidth(2)
        c.roundRect(card_x, card_y, card_width, card_height, 10, fill=1, stroke=1)
        
        # Cabeçalho do card
        c.setFillColorRGB(0, 0.212, 0.373)  # Azul da marca
        c.roundRect(card_x, card_y + card_height - 32, card_width, 32, 10, fill=1, stroke=0)
        
        # Título
        c.setFillColorRGB(1, 1, 1)  # Texto branco
        c.setFont("Helvetica-Bold", 14)
        titulo_width = c.stringWidth("CARD DE TRIAGEM", "Helvetica-Bold", 14)
        titulo_x = card_x + (card_width - titulo_width) / 2
        c.drawString(titulo_x, card_y + card_height - 22, "CARD DE TRIAGEM")
        
        # Campos do card
        c.setFillColorRGB(0, 0, 0)  # Texto preto
        c.setFont("Helvetica-Bold", 12)
        
        # Posições dos campos
        campo_y = card_y + card_height - 55
        linha_height = 25
        
        # PA (Pressão Arterial)
        c.setFont("Helvetica-Bold", 12)
        c.drawString(card_x + 15, campo_y, "PA:")
        c.setFont("Helvetica", 11)
        c.drawString(card_x + 40, campo_y, "________ x ________")

        # FC (Frequência Cardíaca) - MESMA LARGURA
        campo_y -= linha_height
        c.setFont("Helvetica-Bold", 12)
        c.drawString(card_x + 15, campo_y, "FC:")
        c.setFont("Helvetica", 11)
        c.drawString(card_x + 40, campo_y, "__________________")

        # ALT (Altura) - MESMA LARGURA
        campo_y -= linha_height
        c.setFont("Helvetica-Bold", 12)
        c.drawString(card_x + 15, campo_y, "ALT:")
        c.setFont("Helvetica", 11)
        c.drawString(card_x + 50, campo_y, "_________________")

        # PESO - MESMA LARGURA
        campo_y -= linha_height
        c.setFont("Helvetica-Bold", 12)
        c.drawString(card_x + 15, campo_y, "PESO:")
        c.setFont("Helvetica", 11)
        c.drawString(card_x + 55, campo_y, "________________")
                    

class TipoExameModerno:
    """Componente moderno para seleção de tipo de exame"""
    
    def __init__(self, page, azul_marca, branco, cinza_escuro, cinza_claro):
        self.page = page
        self.AZUL_MARCA = azul_marca
        self.BRANCO = branco
        self.CINZA_ESCURO = cinza_escuro
        self.CINZA_CLARO = cinza_claro
        self._valor_selecionado = "Admissional"
        self.container = ft.Container()
        self._criar_cards_selecionaveis()
    
    @property
    def value(self):
        return self._valor_selecionado or "Nenhum selecionado"
    
    def _selecionar_tipo(self, tipo):
        """Seleciona um tipo de exame"""
        def handler(e):
            self._valor_selecionado = tipo
            self._atualizar_visual()
            self.page.update()
        return handler
    
    def _criar_card_tipo(self, texto, is_selected=False):
        """Cria um card moderno para tipo de exame"""
        cor_fundo = ft.Colors.with_opacity(0.15, self.AZUL_MARCA) if is_selected else self.BRANCO
        cor_texto = self.AZUL_MARCA if is_selected else self.AZUL_MARCA
        icone = ft.Icons.CHECK_CIRCLE if is_selected else ft.Icons.RADIO_BUTTON_UNCHECKED
        
        return ft.Container(
            content=ft.Column([
                ft.Icon(icone, color=cor_texto, size=16),
                ft.Text(
                    texto, color=cor_texto, size=14, weight=ft.FontWeight.W_600,
                    text_align=ft.TextAlign.CENTER, max_lines=2, overflow=ft.TextOverflow.ELLIPSIS,
                ),
            ], spacing=3, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            padding=ft.padding.all(5),
            border_radius=8,
            bgcolor=cor_fundo,
            border=ft.border.all(1.5, ft.Colors.with_opacity(0.5 if is_selected else 0.3, self.AZUL_MARCA)),
            shadow=ft.BoxShadow(
                spread_radius=0, 
                blur_radius=15 if is_selected else 8,
                color=ft.Colors.with_opacity(0.15 if is_selected else 0.1, self.AZUL_MARCA),
                offset=ft.Offset(0, 5 if is_selected else 2),
            ),
            on_click=self._selecionar_tipo(texto),
            expand=True,
            height=55,
            alignment=ft.alignment.center,
            animate=ft.Animation(300, ft.AnimationCurve.EASE_OUT),
        )
    
    def _atualizar_visual(self):
        """Atualiza o visual dos cards"""
        self._criar_cards_selecionaveis()
    
    def _criar_cards_selecionaveis(self):
        """Cria os cards selecionáveis modernos"""
        tipos_disponiveis = ["Admissional", "Periódico", "Retorno ao Trabalho", "Demissional"]
        
        cards = []
        for tipo in tipos_disponiveis:
            card = self._criar_card_tipo(tipo, tipo == self._valor_selecionado)
            # Adicionar col diretamente ao card
            card.col = {"xs": 12, "sm": 6, "md": 3}
            cards.append(card)
        
        self.container.content = ft.Column([
            ft.ResponsiveRow(
                cards,
                spacing=5, 
                alignment=ft.MainAxisAlignment.SPACE_EVENLY
            ),
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=0)

class InterfaceHistorico:
    """Interface para gerenciamento do histórico de checklists"""
    
    def __init__(self, page, gerenciador_historico, sistema_clinico, callback_carregar_dados):
        self.page = page
        self.historico = gerenciador_historico
        self.sistema = sistema_clinico
        self.callback_carregar_dados = callback_carregar_dados
        
        # Cores do sistema
        self.AZUL_MARCA = "#00365f"
        self.BEGE_MARCA = "#d4a574"
        self.VERDE_MODERNO = "#10b981"
        self.CINZA_ESCURO = "#374151"
        self.CINZA_CLARO = "#f3f4f6"
        self.BRANCO = "#ffffff"
        self.VERMELHO = "#ef4444"
    
    def criar_botao_historico(self):
        """Cria botão para abrir o histórico"""
        return ft.IconButton(
            icon=ft.Icons.HISTORY,
            icon_color=self.BRANCO,
            tooltip="Histórico de Checklists",
            on_click=self.abrir_historico,
            icon_size=24,
        )
    
    def abrir_historico(self, e=None):
        """Abre janela do histórico"""
        busca_field = ft.TextField(
            label="Buscar por nome ou CPF",
            width=300,
            border_color=self.AZUL_MARCA,
            prefix_icon=ft.Icons.SEARCH,
            on_change=lambda e: self.filtrar_historico(e.control.value, lista_historico)
        )
        
        lista_historico = ft.ListView(spacing=8, height=400, auto_scroll=False)
        self.carregar_lista_historico(lista_historico)
        
        dlg_historico = ft.AlertDialog(
            modal=True,
            bgcolor=self.BRANCO,
            title=ft.Row([
                ft.Icon(ft.Icons.HISTORY, color=self.AZUL_MARCA),
                ft.Text("Histórico de Checklists", color=self.AZUL_MARCA, size=18, weight=ft.FontWeight.BOLD),
            ]),
            content=ft.Container(
                content=ft.Column([
                    busca_field,
                    ft.Container(height=10),
                    ft.Text("Clique em um funcionário para carregar seus dados:", size=12, color=self.CINZA_ESCURO),
                    ft.Container(
                        content=lista_historico,
                        border=ft.border.all(1, self.CINZA_CLARO),
                        border_radius=8,
                        padding=10,
                    ),
                ], spacing=8),
                width=700,
                height=500,
            ),
            actions=[ft.TextButton("Fechar", on_click=lambda _: self.page.close(dlg_historico))],
            actions_alignment=ft.MainAxisAlignment.END,
        )

        # Salvar referência do dialog para poder fechar depois
        self.dlg_historico_atual = dlg_historico
        self.page.open(dlg_historico)
    
    def carregar_lista_historico(self, lista_widget, filtro=""):
        """Carrega lista do histórico na interface"""
        lista_widget.controls.clear()
        
        if filtro:
            if filtro.replace('.', '').replace('-', '').isdigit():
                registros = self.historico.buscar_por_cpf(filtro)
            else:
                registros = self.historico.buscar_por_funcionario(filtro)
        else:
            funcionarios = self.historico.obter_funcionarios_unicos()
            registros = []
            for func in funcionarios:
                registros_func = self.historico.buscar_por_funcionario(func['nome'])
                if registros_func:
                    registros.append(registros_func[0])
        
        for registro in registros:
            lista_widget.controls.append(self.criar_item_historico(registro))
        
        if not registros:
            lista_widget.controls.append(
                ft.Container(
                    content=ft.Text(
                        "Nenhum registro encontrado" if filtro else "Histórico vazio",
                        color=self.CINZA_ESCURO, text_align=ft.TextAlign.CENTER,
                    ),
                    alignment=ft.alignment.center, padding=20,
                )
            )
        
        self.page.update()
    
    def filtrar_historico(self, filtro, lista_widget):
        """Filtra histórico conforme busca"""
        self.carregar_lista_historico(lista_widget, filtro)
    
    def criar_item_historico(self, registro):
        """Cria item visual para o histórico"""
        editado_badge = ft.Container(
            content=ft.Text("EDITADO", size=10, color=self.BRANCO, weight=ft.FontWeight.BOLD),
            bgcolor=self.BEGE_MARCA,
            padding=ft.padding.symmetric(horizontal=6, vertical=2),
            border_radius=4,
        ) if registro.get('editado', False) else ft.Container()
        
        return ft.Container(
            content=ft.Row([
                ft.Column([
                    ft.Row([
                        ft.Text(registro['nome'], size=16, weight=ft.FontWeight.BOLD, color=self.AZUL_MARCA),
                        editado_badge,
                    ], spacing=8),
                    ft.Text(f"CPF: {registro['cpf']}", size=12, color=self.CINZA_ESCURO),
                    ft.Text(f"Tipo: {registro['tipo_exame']}", size=12, color=self.CINZA_ESCURO),
                    ft.Text(f"Data: {registro['data_formatada']}", size=12, color=self.CINZA_ESCURO),
                    ft.Text(f"Procedimentos: {len(registro['procedimentos'])}", size=12, color=self.CINZA_ESCURO),
                ], expand=True, spacing=2),
                ft.Column([
                    ft.Row([
                        ft.ElevatedButton(
                            "Carregar", icon=ft.Icons.UPLOAD,
                            on_click=lambda e, reg=registro: self.carregar_dados_funcionario(reg),
                            bgcolor=ft.Colors.with_opacity(0.15, self.VERDE_MODERNO), 
                            color=self.VERDE_MODERNO, width=110, height=35,
                            style=ft.ButtonStyle(
                                shape=ft.RoundedRectangleBorder(radius=6),
                                side=ft.BorderSide(1.5, ft.Colors.with_opacity(0.6, self.VERDE_MODERNO)),
                                shadow_color=ft.Colors.with_opacity(0.2, self.VERDE_MODERNO),
                                elevation=5,
                            )
                        ),
                        ft.ElevatedButton(
                            "PDF", icon=ft.Icons.PICTURE_AS_PDF,
                            on_click=lambda e, reg=registro: self.abrir_pdf_historico(reg),
                            bgcolor=ft.Colors.with_opacity(0.15, self.AZUL_MARCA), 
                            color=self.AZUL_MARCA, width=110, height=35,
                            style=ft.ButtonStyle(
                                shape=ft.RoundedRectangleBorder(radius=6),
                                side=ft.BorderSide(1.5, ft.Colors.with_opacity(0.6, self.AZUL_MARCA)),
                                shadow_color=ft.Colors.with_opacity(0.2, self.AZUL_MARCA),
                                elevation=5,
                            )
                        ),
                    ], spacing=5),
                ], spacing=4),
            ]),
            padding=12, 
            bgcolor=self.BRANCO, 
            border_radius=8,
            border=ft.border.all(1.5, ft.Colors.with_opacity(0.3, self.BEGE_MARCA)),
            shadow=ft.BoxShadow(
                spread_radius=0, blur_radius=8, 
                color=ft.Colors.with_opacity(0.1, self.AZUL_MARCA), 
                offset=ft.Offset(0, 2)
            ),
        )
    
    def carregar_dados_funcionario(self, registro):
        """Carrega dados do funcionário nos campos principais E FECHA A JANELA"""
        dados = {
            'nome': registro['nome'],
            'cpf': registro['cpf'],
            'tipo_exame': registro['tipo_exame'],
            'procedimentos': registro['procedimentos']
        }
        
        # Carregar os dados na tela principal
        self.callback_carregar_dados(dados)
        
        # FECHAR a janela de histórico - usando referência salva
        if hasattr(self, 'dlg_historico_atual'):
            self.page.close(self.dlg_historico_atual)
        
        # Mostrar confirmação
        self.page.snack_bar = ft.SnackBar(
            content=ft.Text(f"Dados de {registro['nome']} carregados!", color=self.BRANCO),
            bgcolor=self.VERDE_MODERNO,
        )
        self.page.snack_bar.open = True
        self.page.update()
        
    def abrir_pdf_historico(self, registro):
        """Abre o PDF do histórico para impressão (igual ao botão Imprimir)"""
        try:
            filename = registro['arquivo_pdf']
            if os.path.exists(filename):
                # Abrir PDF igual ao botão Imprimir da tela principal
                if platform.system() == 'Windows':
                    os.startfile(filename)
                elif platform.system() == 'Darwin':
                    subprocess.Popen(['open', filename])
                else:
                    subprocess.Popen(['xdg-open', filename])
                    
            else:
                # Se não tem PDF, gerar um novo
                sistema_temp = SistemaClinico()
                filename = sistema_temp.gerar_pdf_checklist(
                    registro['nome'], 
                    registro['cpf'], 
                    registro['tipo_exame'], 
                    registro['procedimentos']
                )
                
                # Abrir o PDF gerado
                if platform.system() == 'Windows':
                    os.startfile(filename)
                elif platform.system() == 'Darwin':
                    subprocess.Popen(['open', filename])
                else:
                    subprocess.Popen(['xdg-open', filename])
            
        except Exception as ex:
            print(f"Erro ao abrir PDF: {ex}")

# =================== CLASSE PRINCIPAL DA INTERFACE ===================

class GerenciadorInterface:
    """Gerencia toda a interface do usuário e interações"""
    
    def __init__(self, page):
        self.page = page
        self.sistema = SistemaClinico()
        self.historico = GerenciadorHistorico()
        self.logger = GerenciadorLogs()
        self.procedimentos_selecionados = []
        
        # Configurar página
        self._configurar_pagina()
        
        # Inicializar componentes
        self._inicializar_componentes()
        
        # Configurar interface do histórico
        self.interface_historico = InterfaceHistorico(
            self.page, self.historico, self.sistema, self.carregar_dados_do_historico
        )
    
    def _configurar_pagina(self):
        """Configura propriedades da página"""
        self.page.title = ConfigSistema.WINDOW_TITLE
        self.page.theme_mode = ft.ThemeMode.LIGHT
        self.page.window.maximized = True
        self.page.padding = 15
        self.page.scroll = None
        self.page.bgcolor = ConfigSistema.WINDOW_BGCOLOR
    
    def _inicializar_componentes(self):
        """Inicializa todos os componentes da interface"""
        # Container para logo
        self.logo_container = ft.Container()
        self._atualizar_logo()
        
        # Campos de entrada
        self.nome_field = ft.TextField(
            label="Nome Completo do Funcionário",
            width=350,
            border_color=ft.Colors.with_opacity(0.3, ConfigSistema.AZUL_MARCA),
            focused_border_color=ft.Colors.with_opacity(0.5, ConfigSistema.AZUL_MARCA),
            prefix_icon=ft.Icons.PERSON,
            text_style=ft.TextStyle(size=14),
            label_style=ft.TextStyle(color=ConfigSistema.CINZA_ESCURO),
        )
        
        self.cpf_field = ft.TextField(
            label="CPF do Funcionário",
            width=200,
            border_color=ft.Colors.with_opacity(0.3, ConfigSistema.AZUL_MARCA),
            focused_border_color=ft.Colors.with_opacity(0.5, ConfigSistema.AZUL_MARCA),
            prefix_icon=ft.Icons.BADGE,
            max_length=14,
            tooltip="Digite apenas números do CPF",
            on_change=self._aplicar_mascara_cpf,
            text_style=ft.TextStyle(size=14),
            label_style=ft.TextStyle(color=ConfigSistema.CINZA_ESCURO),
        )
        
        # Componente de tipo de exame
        self.tipo_exame_dropdown = TipoExameModerno(
            self.page, ConfigSistema.AZUL_MARCA, ConfigSistema.BRANCO, 
            ConfigSistema.CINZA_ESCURO, ConfigSistema.CINZA_CLARO
        )
        
        # Campo para novos procedimentos
        self.novo_procedimento_field = ft.TextField(
            label="Nome do Novo Procedimento",
            width=280,
            border_color=ft.Colors.with_opacity(0.3, ConfigSistema.AZUL_MARCA),
            focused_border_color=ft.Colors.with_opacity(0.5, ConfigSistema.AZUL_MARCA),
            prefix_icon=ft.Icons.MEDICAL_SERVICES,
            text_style=ft.TextStyle(size=14),
            label_style=ft.TextStyle(color=ConfigSistema.CINZA_ESCURO),
        )
        
        # Campo de busca
        self.busca_field = ft.TextField(
            label="Buscar Procedimentos",
            width=350,
            border_color=ft.Colors.with_opacity(0.3, ConfigSistema.AZUL_MARCA),
            focused_border_color=ft.Colors.with_opacity(0.5, ConfigSistema.AZUL_MARCA),
            prefix_icon=ft.Icons.SEARCH,
            on_change=lambda e: self._filtrar_procedimentos(e.control.value),
            text_style=ft.TextStyle(size=14),
            label_style=ft.TextStyle(color=ConfigSistema.CINZA_ESCURO),
        )
        
        # Listas
        self.lista_procedimentos = ft.ListView(spacing=6, height=350, auto_scroll=False)
        self.lista_selecionados = ft.ListView(spacing=6, height=350, auto_scroll=False)
        
        # Inicializar listas
        self._atualizar_lista_procedimentos()

        # LIMPAR e FORÇAR todos os obrigatórios novamente
        self.procedimentos_selecionados.clear()
        self.procedimentos_selecionados.extend(self.sistema.procedimentos_obrigatorios)

        self._ordenar_procedimentos()  # Garantir ordem correta
        self._atualizar_lista_selecionados()
    
    def _aplicar_mascara_cpf(self, e):
        """Aplica máscara no CPF e valida"""
        cpf_formatado = self.sistema.formatar_cpf(e.control.value)
        e.control.value = cpf_formatado
        
        cpf_limpo = re.sub(r'[^0-9]', '', cpf_formatado)
        if len(cpf_limpo) == 11:
            if self.sistema.validar_cpf(cpf_limpo):
                e.control.border_color = ft.Colors.with_opacity(0.6, "#059669")
                self._verificar_cpf_no_historico(cpf_formatado)
            else:
                e.control.border_color = ft.Colors.with_opacity(0.6, ConfigSistema.VERMELHO)
        else:
            e.control.border_color = ft.Colors.with_opacity(0.3, ConfigSistema.AZUL_MARCA)
        
        self.page.update()
    
    def _verificar_cpf_no_historico(self, cpf):
        """Verifica se CPF existe no histórico e sugere carregar dados"""
        registros = self.historico.buscar_por_cpf(cpf)
        
        if registros:
            ultimo_registro = registros[0]
            
            def carregar_dados_sugeridos(e):
                self.carregar_dados_do_historico({
                    'nome': ultimo_registro['nome'],
                    'cpf': ultimo_registro['cpf'],
                    'tipo_exame': ultimo_registro['tipo_exame'],
                    'procedimentos': ultimo_registro['procedimentos']
                })
                self.page.close(dlg_sugestao)
            
            def ignorar_sugestao(e):
                self.page.close(dlg_sugestao)
            
            dlg_sugestao = ft.AlertDialog(
                title=ft.Text("Funcionário Encontrado!", color=ConfigSistema.VERDE_MODERNO),
                content=ft.Text(
                    f"Encontramos '{ultimo_registro['nome']}' no histórico.\n"
                    f"Último exame: {ultimo_registro['tipo_exame']}\n"
                    f"Data: {ultimo_registro['data_formatada']}\n\n"
                    "Deseja carregar os dados?"
                ),
                actions=[
                    ft.TextButton("Não", on_click=ignorar_sugestao),
                    ft.ElevatedButton("Sim, Carregar", on_click=carregar_dados_sugeridos, 
                                    bgcolor=ConfigSistema.VERDE_MODERNO, color=ConfigSistema.BRANCO),
                ],
            )
            self.page.open(dlg_sugestao)
    
    def carregar_dados_do_historico(self, dados):
        """Carrega dados do histórico nos campos do formulário"""
        self.nome_field.value = dados['nome']
        self.cpf_field.value = dados['cpf']
        self.tipo_exame_dropdown._valor_selecionado = dados['tipo_exame']
        self.tipo_exame_dropdown._atualizar_visual()
        
        self.procedimentos_selecionados.clear()
        self.procedimentos_selecionados.extend(dados['procedimentos'])
        
        self._atualizar_lista_selecionados()
        self.page.update()
    
    def _atualizar_logo(self):
        """Atualiza o logo no cabeçalho"""
        if self.sistema.logo_path and os.path.exists(self.sistema.logo_path):
            try:
                with open(self.sistema.logo_path, "rb") as f:
                    logo_data = base64.b64encode(f.read()).decode()
                
                self.logo_container.content = ft.Image(
                    src_base64=logo_data,
                    width=250,
                    height=45,
                    fit=ft.ImageFit.FIT_WIDTH,
                )
            except:
                self._criar_logo_placeholder()
        else:
            self._criar_logo_placeholder()
    
    def _criar_logo_placeholder(self):
        """Cria logo placeholder"""
        self.logo_container.content = ft.Container(
            content=ft.Row([
                ft.Text("LABORE", color=ConfigSistema.BRANCO, size=26, weight=ft.FontWeight.BOLD),
                ft.Text("PLUS", color=ConfigSistema.BEGE_MARCA, size=26, weight=ft.FontWeight.BOLD),
            ], spacing=5, alignment=ft.MainAxisAlignment.START),
            width=250,
            height=45,
            alignment=ft.alignment.center_left,
            padding=ft.padding.only(left=20),
        )
    
    def _mostrar_snackbar(self, mensagem, cor):
        """Mostra mensagem de feedback"""
        self.page.snack_bar = ft.SnackBar(
            content=ft.Text(mensagem, color=ConfigSistema.BRANCO, size=14, weight=ft.FontWeight.W_500),
            bgcolor=cor,
            duration=3000,
        )
        self.page.snack_bar.open = True
        self.page.update()
    
    def _filtrar_procedimentos(self, filtro):
        """Filtra procedimentos conforme busca"""
        self._atualizar_lista_procedimentos(filtro)

    def _atualizar_lista_procedimentos(self, filtro=""):
        """Atualiza lista de procedimentos disponíveis"""
        self.lista_procedimentos.controls.clear()
        
        procedimentos_filtrados = [p for p in self.sistema.lista_procedimentos 
                         if filtro.lower() in p.lower()]
        
        for procedimento in procedimentos_filtrados:
            self.lista_procedimentos.controls.append(
                self._criar_item_lista(procedimento, False)
            )
        
        self.page.update()

    def _atualizar_lista_selecionados(self):
        """Atualiza lista de procedimentos selecionados"""
        self.lista_selecionados.controls.clear()
        
        for procedimento in self.procedimentos_selecionados:
            self.lista_selecionados.controls.append(
                self._criar_item_lista(procedimento, True)
            )
        
        self.page.update()

    def _criar_item_lista(self, procedimento, is_selecionado=False):
        """Cria item visual para as listas de procedimentos"""
        is_obrigatorio = procedimento in self.sistema.procedimentos_obrigatorios
        cor_icone = "#FFD700" if is_obrigatorio else (ConfigSistema.VERDE_MODERNO if is_selecionado else ConfigSistema.AZUL_MARCA)
        icone = ft.Icons.STAR if is_obrigatorio else (ft.Icons.CHECK_CIRCLE if is_selecionado else ft.Icons.MEDICAL_SERVICES)
        
        # Botões de ação
        if is_selecionado:
            botoes = [
                ft.IconButton(
                    icon=ft.Icons.REMOVE_CIRCLE,
                    icon_color=ConfigSistema.VERMELHO,
                    icon_size=18,
                    tooltip="Remover",
                    on_click=lambda e, p=procedimento: self._remover_procedimento(p)
                ),
            ]
        else:
            botoes = [
                ft.IconButton(
                    icon=ft.Icons.STAR_BORDER if not is_obrigatorio else ft.Icons.STAR,
                    icon_color="#FFD700",
                    icon_size=16,
                    tooltip="Marcar como Obrigatório" if not is_obrigatorio else "Remover Obrigatório",
                    on_click=lambda e, p=procedimento: self._alternar_obrigatorio(p)
                ),
                ft.IconButton(
                    icon=ft.Icons.ADD_CIRCLE,
                    icon_color=ConfigSistema.VERDE_MODERNO,
                    icon_size=18,
                    tooltip="Adicionar",
                    on_click=lambda e, p=procedimento: self._adicionar_procedimento(p)
                ),
                ft.IconButton(
                    icon=ft.Icons.EDIT,
                    icon_color=ConfigSistema.AZUL_MARCA,
                    icon_size=16,
                    tooltip="Editar",
                    on_click=lambda e, p=procedimento: self._editar_procedimento(p)
                ),
                ft.IconButton(
                    icon=ft.Icons.DELETE,
                    icon_color=ConfigSistema.VERMELHO,
                    icon_size=16,
                    tooltip="Excluir",
                    on_click=lambda e, p=procedimento: self._excluir_procedimento(p)
                )
            ]
        
        return ft.Container(
            content=ft.Row([
                ft.Row([
                    ft.Icon(icone, color=cor_icone, size=18),
                    ft.Container(
                        content=ft.Text(
                            procedimento,
                            size=16,
                            weight=ft.FontWeight.W_600 if is_obrigatorio else ft.FontWeight.W_400,
                            color=ConfigSistema.CINZA_ESCURO,
                            overflow=ft.TextOverflow.ELLIPSIS,
                        ),
                        expand=True,
                    )
                ], spacing=8, expand=True),
                ft.Row(botoes, spacing=2)
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            padding=ft.padding.symmetric(horizontal=12, vertical=8),
            border_radius=8,
            bgcolor=ConfigSistema.BRANCO,
            border=ft.border.all(1.5, ft.Colors.with_opacity(0.3, ConfigSistema.AZUL_MARCA)),
            shadow=ft.BoxShadow(
                spread_radius=0,
                blur_radius=8,
                color=ft.Colors.with_opacity(0.1, ConfigSistema.AZUL_MARCA),
                offset=ft.Offset(0, 2),
            ),
        )
        
    def _adicionar_procedimento(self, procedimento):
        """Adiciona procedimento à lista de selecionados"""
        if procedimento not in self.procedimentos_selecionados:
            self.procedimentos_selecionados.append(procedimento)
            self._atualizar_lista_selecionados()

    def _remover_procedimento(self, procedimento):
        """Remove procedimento da lista de selecionados"""
        if procedimento in self.procedimentos_selecionados:
            self.procedimentos_selecionados.remove(procedimento)
            self._atualizar_lista_selecionados()

    def _alternar_obrigatorio(self, procedimento):
        """Alterna status obrigatório de um procedimento"""
        if self.sistema.alternar_obrigatorio(procedimento):
            self._atualizar_lista_procedimentos()
            if procedimento in self.procedimentos_selecionados:
                self._atualizar_lista_selecionados()
            
            # Se virou obrigatório, adicionar automaticamente
            if procedimento in self.sistema.procedimentos_obrigatorios and procedimento not in self.procedimentos_selecionados:
                self.procedimentos_selecionados.append(procedimento)
                self._atualizar_lista_selecionados()
            
            self._mostrar_snackbar(f"Procedimento '{procedimento}' alterado!", ConfigSistema.VERDE_MODERNO)
        else:
            self._mostrar_snackbar("Erro ao alterar procedimento!", ConfigSistema.VERMELHO)

    def _adicionar_novo_procedimento(self, e):
        """Adiciona novo procedimento ao sistema com pergunta sobre laudo"""
        procedimento = self.novo_procedimento_field.value.strip()
        
        if not procedimento:
            self._mostrar_snackbar("Digite o nome do procedimento!", ConfigSistema.VERMELHO)
            return
        
        if procedimento in self.sistema.procedimentos_db:
            self._mostrar_snackbar("Procedimento já existe!", ConfigSistema.VERMELHO)
            return
        
        # Perguntar sobre laudo
        def confirmar_adicao(requer_laudo):
            if self.sistema.adicionar_procedimento(procedimento):
                # Definir se requer laudo
                self.sistema.definir_requer_laudo(procedimento, requer_laudo)
                
                self.novo_procedimento_field.value = ""
                self._atualizar_lista_procedimentos()
                self.page.update()
                
                laudo_texto = " (com laudo)" if requer_laudo else " (sem laudo)"
                self._mostrar_snackbar(f"Procedimento '{procedimento}' adicionado{laudo_texto}!", ConfigSistema.VERDE_MODERNO)
                
                self.page.close(dlg_laudo)
            else:
                self._mostrar_snackbar("Erro ao adicionar procedimento!", ConfigSistema.VERMELHO)
        
        # Dialog para perguntar sobre laudo
        dlg_laudo = ft.AlertDialog(
            modal=True,
            bgcolor=ConfigSistema.BRANCO,
            title=ft.Row([
                ft.Icon(ft.Icons.HELP_OUTLINE, color=ConfigSistema.AZUL_MARCA),
                ft.Text("Configuração do Procedimento", color=ConfigSistema.AZUL_MARCA, size=16, weight=ft.FontWeight.BOLD),
            ], alignment=ft.MainAxisAlignment.CENTER),
            content=ft.Container(
                content=ft.Column([
                    ft.Text(f"Procedimento: {procedimento}", size=14, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER),
                    ft.Container(height=10),
                    ft.Text("Este procedimento precisa da impressão do laudo?", size=13, text_align=ft.TextAlign.CENTER),
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                width=350,
                height=80,
            ),
            actions=[
                ft.Row([
                    ft.ElevatedButton(
                        "NÃO", 
                        on_click=lambda _: confirmar_adicao(False),
                        bgcolor=ft.Colors.with_opacity(0.15, ConfigSistema.CINZA_ESCURO), 
                        color=ConfigSistema.CINZA_ESCURO,
                        width=120,
                    ),
                    ft.ElevatedButton(
                        "SIM", 
                        on_click=lambda _: confirmar_adicao(True),
                        bgcolor=ConfigSistema.VERDE_MODERNO, 
                        color=ConfigSistema.BRANCO,
                        width=120,
                    ),
                ], alignment=ft.MainAxisAlignment.CENTER, spacing=10)
            ],
            actions_alignment=ft.MainAxisAlignment.CENTER,
        )
        
        self.page.open(dlg_laudo)

    def _editar_procedimento(self, procedimento_antigo):
        """Abre dialog para editar procedimento com toggle de laudo"""
        
        # Estado inicial do toggle
        requer_laudo_inicial = self.sistema.procedimento_requer_laudo(procedimento_antigo)
        
        def fechar_dialog():
            self.page.close(dlg_modal)
        
        def toggle_laudo_changed(e):
            # Atualizar o estado interno quando o toggle muda
            nonlocal requer_laudo_atual
            requer_laudo_atual = e.control.value
        
        def salvar_edicao():
            novo_nome = dialog_field.value.strip()
            if not novo_nome:
                self._mostrar_snackbar("Nome não pode estar vazio!", ConfigSistema.VERMELHO)
                return
                
            # Salvar nome
            if self.sistema.editar_procedimento_db(procedimento_antigo, novo_nome):
                # Salvar configuração de laudo
                self.sistema.definir_requer_laudo(novo_nome, requer_laudo_atual)
                
                # Atualizar listas se o procedimento estiver selecionado
                if procedimento_antigo in self.procedimentos_selecionados:
                    index = self.procedimentos_selecionados.index(procedimento_antigo)
                    self.procedimentos_selecionados[index] = novo_nome
                    self._atualizar_lista_selecionados()
                
                self._atualizar_lista_procedimentos()
                
                laudo_texto = " (com laudo)" if requer_laudo_atual else " (sem laudo)"
                self._mostrar_snackbar(f"Procedimento editado{laudo_texto}!", ConfigSistema.VERDE_MODERNO)
                fechar_dialog()
            else:
                self._mostrar_snackbar("Nome inválido ou já existe!", ConfigSistema.VERMELHO)
        
        # Estado atual do toggle
        requer_laudo_atual = requer_laudo_inicial
        
        # Campo de nome
        dialog_field = ft.TextField(
            value=procedimento_antigo,
            label="Nome do Procedimento",
            width=400,
            border_color=ConfigSistema.AZUL_MARCA,
            text_style=ft.TextStyle(size=14),
        )
        
        # Toggle switch para laudo
        toggle_laudo = ft.Switch(
            label="Precisa da impressão do laudo?",
            value=requer_laudo_inicial,
            on_change=toggle_laudo_changed,
            active_color=ConfigSistema.VERDE_MODERNO,
            inactive_track_color=ConfigSistema.CINZA_CLARO,
        )
        
        dlg_modal = ft.AlertDialog(
            modal=True,
            bgcolor=ConfigSistema.BRANCO,
            title=ft.Row([
                ft.Icon(ft.Icons.EDIT, color=ConfigSistema.AZUL_MARCA),
                ft.Text("Editar Procedimento", color=ConfigSistema.AZUL_MARCA, size=18, weight=ft.FontWeight.BOLD),
            ], alignment=ft.MainAxisAlignment.CENTER),
            content=ft.Container(
                content=ft.Column([
                    dialog_field,
                    ft.Container(height=15),
                    ft.Container(
                        content=toggle_laudo,
                        bgcolor=ft.Colors.with_opacity(0.05, ConfigSistema.AZUL_MARCA),
                        padding=ft.padding.all(10),
                        border_radius=8,
                        border=ft.border.all(1, ft.Colors.with_opacity(0.2, ConfigSistema.AZUL_MARCA)),
                    ),
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                width=450,
                height=140,
            ),
            actions=[
                ft.Row([
                    ft.TextButton("Cancelar", on_click=lambda _: fechar_dialog()),
                    ft.ElevatedButton("Salvar", on_click=lambda _: salvar_edicao(), 
                                    bgcolor=ConfigSistema.AZUL_MARCA, color=ConfigSistema.BRANCO),
                ], alignment=ft.MainAxisAlignment.END, spacing=10)
            ],
            actions_alignment=ft.MainAxisAlignment.CENTER,
        )
        
        self.page.open(dlg_modal)

    def _excluir_procedimento(self, procedimento):
        """Abre dialog para confirmar exclusão"""
        def fechar_dialog():
            self.page.close(dlg_modal)
        
        def confirmar_exclusao():
            if self.sistema.remover_procedimento_db(procedimento):
                if procedimento in self.procedimentos_selecionados:
                    self.procedimentos_selecionados.remove(procedimento)
                    self._atualizar_lista_selecionados()
                
                self._atualizar_lista_procedimentos()
                self._mostrar_snackbar("Procedimento excluído com sucesso!", ConfigSistema.VERDE_MODERNO)
            else:
                self._mostrar_snackbar("Erro ao excluir procedimento!", ConfigSistema.VERMELHO)
            
            fechar_dialog()
        
        dlg_modal = ft.AlertDialog(
            modal=True,
            title=ft.Text("Confirmar Exclusão", color=ConfigSistema.VERMELHO, size=18, weight=ft.FontWeight.BOLD),
            content=ft.Text(f"Deseja realmente excluir o procedimento '{procedimento}'?", 
                          color=ConfigSistema.CINZA_ESCURO, size=14),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda _: fechar_dialog()),
                ft.ElevatedButton("Excluir", on_click=lambda _: confirmar_exclusao(), 
                                bgcolor=ConfigSistema.VERMELHO, color=ConfigSistema.BRANCO),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        
        self.page.open(dlg_modal)

    def _adicionar_obrigatorios(self, e):
        """Adiciona todos os procedimentos obrigatórios à lista"""
        adicionados = []
        for proc_obrig in self.sistema.procedimentos_obrigatorios:
            if proc_obrig not in self.procedimentos_selecionados:
                self.procedimentos_selecionados.append(proc_obrig)
                adicionados.append(proc_obrig)
        
        if adicionados:
            self._ordenar_procedimentos()  # Garantir ordem correta
            self._atualizar_lista_selecionados()
            self._mostrar_snackbar(f"Procedimentos adicionados: {', '.join(adicionados)}", ConfigSistema.VERDE_MODERNO)
        else:
            self._mostrar_snackbar("Todos os procedimentos obrigatórios já estão na lista!", ConfigSistema.AZUL_MARCA)

    def _limpar_procedimentos(self, e):
        """Limpa apenas os procedimentos selecionados"""
        self.procedimentos_selecionados.clear()
        self._atualizar_lista_selecionados()
        self._mostrar_snackbar("Procedimentos limpos!", ConfigSistema.VERDE_MODERNO)

    def _limpar_tudo(self, e):
        """Limpa todos os dados do formulário e deixa apenas obrigatórios"""
        # Limpar dados pessoais
        self.nome_field.value = ""
        self.cpf_field.value = ""
        self.cpf_field.border_color = ft.Colors.with_opacity(0.3, ConfigSistema.AZUL_MARCA)
        
        # Resetar tipo de exame para padrão
        self.tipo_exame_dropdown._valor_selecionado = "Admissional"
        self.tipo_exame_dropdown._atualizar_visual()
        
        # Limpar procedimentos e adicionar apenas obrigatórios
        self.procedimentos_selecionados.clear()
        self.procedimentos_selecionados.extend(self.sistema.procedimentos_obrigatorios)
        
        # Limpar busca
        self.busca_field.value = ""
        
        # Atualizar interface
        self._atualizar_lista_selecionados()
        self._atualizar_lista_procedimentos()
        self.page.update()
        
        self._mostrar_snackbar("Formulário limpo! Apenas procedimentos obrigatórios mantidos.", ConfigSistema.VERDE_MODERNO)

    def _configurar_logo(self, e):
        """Abre dialog para configurar logos"""
        def fechar_config():
            self.page.close(dlg_config)
        
        def upload_logo_tela(e):
            if e.files and len(e.files) > 0:
                try:
                    file_path = e.files[0].path
                    file_name = e.files[0].name
                    
                    if file_name.lower().endswith(('.png', '.jpg', '.jpeg')):
                        new_path = f"logo_tela.{file_name.split('.')[-1]}"
                        shutil.copy2(file_path, new_path)
                        
                        self.sistema.logo_path = new_path
                        self.sistema.salvar_config()
                        self._atualizar_logo()
                        self._mostrar_snackbar("Logo da tela atualizado!", ConfigSistema.VERDE_MODERNO)
                        fechar_config()
                    else:
                        self._mostrar_snackbar("Apenas arquivos PNG ou JPG!", ConfigSistema.VERMELHO)
                except (AttributeError, IndexError, IOError) as ex:
                    self._mostrar_snackbar(f"Erro ao processar arquivo: {str(ex)}", ConfigSistema.VERMELHO)
            else:
                self._mostrar_snackbar("Nenhum arquivo selecionado!", ConfigSistema.VERMELHO)

        def upload_logo_pdf(e):
            if e.files and len(e.files) > 0:
                try:
                    file_path = e.files[0].path
                    file_name = e.files[0].name
                    
                    if file_name.lower().endswith(('.png', '.jpg', '.jpeg')):
                        new_path = f"logo_pdf.{file_name.split('.')[-1]}"
                        shutil.copy2(file_path, new_path)
                        
                        self.sistema.logo_pdf_path = new_path
                        self.sistema.salvar_config()
                        self._mostrar_snackbar("Logo do PDF atualizado!", ConfigSistema.VERDE_MODERNO)
                        fechar_config()
                    else:
                        self._mostrar_snackbar("Apenas arquivos PNG ou JPG!", ConfigSistema.VERMELHO)
                except (AttributeError, IndexError, IOError) as ex:
                    self._mostrar_snackbar(f"Erro ao processar arquivo: {str(ex)}", ConfigSistema.VERMELHO)
            else:
                self._mostrar_snackbar("Nenhum arquivo selecionado!", ConfigSistema.VERMELHO)
        
        file_picker_tela = ft.FilePicker(on_result=upload_logo_tela)
        file_picker_pdf = ft.FilePicker(on_result=upload_logo_pdf)
        self.page.overlay.append(file_picker_tela)
        self.page.overlay.append(file_picker_pdf)
        self.page.update()
        
        dlg_config = ft.AlertDialog(
            modal=True,
            bgcolor=ConfigSistema.BRANCO,  # Fundo branco
            title=ft.Row([
                ft.Icon(ft.Icons.SETTINGS, color=ConfigSistema.AZUL_MARCA),
                ft.Text("Configurar Logos", color=ConfigSistema.AZUL_MARCA, size=18, weight=ft.FontWeight.BOLD),
            ], alignment=ft.MainAxisAlignment.CENTER),  # Título centralizado
            content=ft.Container(
                content=ft.Column([
                    ft.Text("Logo para a Tela do Sistema:", size=14, weight=ft.FontWeight.BOLD, 
                        color=ConfigSistema.CINZA_ESCURO, text_align=ft.TextAlign.CENTER),
                    ft.ElevatedButton(
                        "Escolher Logo da Tela",
                        icon=ft.Icons.COMPUTER,
                        on_click=lambda _: file_picker_tela.pick_files(
                            allowed_extensions=["png", "jpg", "jpeg"],
                            dialog_title="Logo para a tela do sistema"
                        ),
                        bgcolor=ConfigSistema.AZUL_MARCA,
                        color=ConfigSistema.BRANCO,
                        width=300,
                    ),
                    ft.Container(height=15),
                    ft.Text("Logo para o PDF (Impressão):", size=14, weight=ft.FontWeight.BOLD,
                        color=ConfigSistema.CINZA_ESCURO, text_align=ft.TextAlign.CENTER),
                    ft.ElevatedButton(
                        "Escolher Logo do PDF",
                        icon=ft.Icons.PICTURE_AS_PDF,
                        on_click=lambda _: file_picker_pdf.pick_files(
                            allowed_extensions=["png", "jpg", "jpeg"],
                            dialog_title="Logo para o PDF"
                        ),
                        bgcolor=ConfigSistema.VERDE_MODERNO,
                        color=ConfigSistema.BRANCO,
                        width=300,
                    ),
                ], spacing=15, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                width=380,
                height=180,
                bgcolor=ConfigSistema.BRANCO,  # Fundo branco para o container também
                alignment=ft.alignment.center,
            ),
            actions=[
                ft.TextButton("Fechar", on_click=lambda _: fechar_config(), 
                            style=ft.ButtonStyle(color=ConfigSistema.AZUL_MARCA)),
            ],
            actions_alignment=ft.MainAxisAlignment.CENTER,  # Botão centralizado
        )
        
        self.page.open(dlg_config)

    def _validar_dados_avancado(self):
        """Validação avançada de dados"""
        nome = self.nome_field.value.strip()
        cpf = self.cpf_field.value.strip()
        tipo_exame = self.tipo_exame_dropdown.value
        
        # Validar nome
        nome_valido, erro_nome = ValidadorAvancado.validar_nome_completo(nome)
        if not nome_valido:
            self._mostrar_snackbar(erro_nome, ConfigSistema.VERMELHO)
            return False
        
        # Validar CPF
        cpf_limpo = re.sub(r'[^0-9]', '', cpf)
        if not self.sistema.validar_cpf(cpf_limpo):
            self._mostrar_snackbar("CPF inválido! Verifique os dados.", ConfigSistema.VERMELHO)
            return False
        
        # Validar procedimentos mínimos
        proc_valido, erro_proc = ValidadorAvancado.validar_procedimentos_minimos(
            self.procedimentos_selecionados, self.sistema.procedimentos_obrigatorios
        )
        if not proc_valido:
            self._mostrar_snackbar(erro_proc, ConfigSistema.VERMELHO)
            return False
        
        # Validar compatibilidade
        compat_valido, erro_compat = ValidadorAvancado.validar_compatibilidade_tipo_procedimentos(
            tipo_exame, self.procedimentos_selecionados
        )
        if not compat_valido:
            self._mostrar_snackbar(erro_compat, ConfigSistema.VERMELHO)
            return False
        
        return True

    def _garantir_procedimentos_obrigatorios(self):
        """Garante que procedimentos obrigatórios estejam na lista"""
        for proc_obrig in self.sistema.procedimentos_obrigatorios:
            if proc_obrig not in self.procedimentos_selecionados:
                self.procedimentos_selecionados.append(proc_obrig)
        
        # Ordenar: Triagem primeiro, Faturamento último
        self._ordenar_procedimentos()
        self._atualizar_lista_selecionados()

    def _ordenar_procedimentos(self):
        """Ordena procedimentos: Triagem primeiro, Faturamento último"""
        if not self.procedimentos_selecionados:
            return
        
        # Separar procedimentos especiais
        triagem = "Triagem" if "Triagem" in self.procedimentos_selecionados else None
        faturamento = "Faturamento" if "Faturamento" in self.procedimentos_selecionados else None
        
        # Remover da lista atual
        if triagem:
            self.procedimentos_selecionados.remove("Triagem")
        if faturamento:
            self.procedimentos_selecionados.remove("Faturamento")
        
        # Reordenar: Triagem primeiro
        if triagem:
            self.procedimentos_selecionados.insert(0, "Triagem")
        
        # Faturamento último
        if faturamento:
            self.procedimentos_selecionados.append("Faturamento")

    def _gerar_checklist(self, e):
        """Gera PDF do checklist e abre para impressão"""
        if not self._validar_dados_avancado():
            return
        
        nome = self.nome_field.value.strip()
        cpf = self.cpf_field.value.strip()
        tipo_exame = self.tipo_exame_dropdown.value
        
        self._garantir_procedimentos_obrigatorios()
        
        if not self.procedimentos_selecionados:
            self._mostrar_snackbar("Selecione pelo menos um procedimento!", ConfigSistema.VERMELHO)
            return
        
        try:
            # Gerar PDF
            filename = self.sistema.gerar_pdf_checklist(nome, cpf, tipo_exame, self.procedimentos_selecionados)
            
            # Log da operação
            self.logger.log_geracao_pdf(nome, cpf, tipo_exame, self.procedimentos_selecionados, filename)
            
            # Salvar no histórico
            checklist_id = self.historico.adicionar_checklist(
                nome, cpf, tipo_exame, self.procedimentos_selecionados, filename
            )
            
            self.logger.log_historico("Checklist adicionado", nome, f"ID: {checklist_id}")
            
            self._mostrar_snackbar(f"PDF gerado e salvo! ID: {checklist_id}", ConfigSistema.VERDE_MODERNO)
            
            # Abrir PDF diretamente
            self._abrir_pdf(filename)
                    
        except Exception as ex:
            self.logger.log_erro("Geração de PDF", ex)
            self._mostrar_snackbar(f"Erro ao gerar PDF: {str(ex)}", ConfigSistema.VERMELHO)

    def _abrir_pdf(self, filename):
        """Abre PDF no visualizador padrão"""
        try:
            if platform.system() == 'Windows':
                os.startfile(filename)
            elif platform.system() == 'Darwin':
                subprocess.Popen(['open', filename])
            else:
                subprocess.Popen(['xdg-open', filename])
        except:
            pass
        
    def _abrir_pdf_para_impressao(self, filename):
        """Abre PDF diretamente para impressão"""
        try:
            if platform.system() == 'Windows':
                # No Windows, abrir PDF com comando de impressão
                os.startfile(filename, 'print')
            elif platform.system() == 'Darwin':
                # No Mac, abrir PDF
                subprocess.Popen(['open', filename])
            else:
                # No Linux, abrir PDF
                subprocess.Popen(['xdg-open', filename])
        except Exception as e:
            # Se falhar, usar método normal
            self._abrir_pdf(filename)
    
    def construir_interface(self):
        """Interface completa com todas as melhorias"""
        return ft.Column([
            # BARRA DE NAVEGAÇÃO SUPERIOR
            ft.Container(
                content=ft.Row([
                    self.logo_container,
                    ft.Container(expand=True),
                    ft.Container(
                        content=ft.Row([
                            ft.Text("CHECKLIST", size=18, weight=ft.FontWeight.W_600, color=ConfigSistema.BRANCO),
                            self.interface_historico.criar_botao_historico(),  # Histórico
                            ft.IconButton(
                                icon=ft.Icons.SETTINGS,
                                icon_color=ConfigSistema.BRANCO,
                                tooltip="Configurar Logos",
                                on_click=self._configurar_logo,
                                icon_size=24,
                            ),
                            ft.IconButton(
                                icon=ft.Icons.INFO_OUTLINE,
                                icon_color=ConfigSistema.BRANCO,
                                tooltip="Sobre o Sistema",
                                icon_size=24,
                            ),
                        ], spacing=8, alignment=ft.MainAxisAlignment.END),
                        padding=ft.padding.only(right=10),
                    ),
                ]),
                bgcolor=ft.Colors.with_opacity(0.85, ConfigSistema.AZUL_MARCA),
                border=ft.border.all(1, ft.Colors.with_opacity(0.3, ConfigSistema.BRANCO)),
                shadow=ft.BoxShadow(
                    spread_radius=0,
                    blur_radius=10,
                    color=ft.Colors.with_opacity(0.2, ConfigSistema.AZUL_MARCA),
                    offset=ft.Offset(0, 3),
                ),
                height=60,
                padding=ft.padding.only(left=15, right=0, top=0, bottom=0),
            ),
            
            # LINHA PRINCIPAL: Cards Principais
            ft.ResponsiveRow([
                # CARD ESQUERDO
                ft.Container(
                    content=ft.Column([
                        # Dados do Funcionário
                        ft.Text("DADOS DO FUNCIONÁRIO", size=16, weight=ft.FontWeight.BOLD, color=ConfigSistema.AZUL_MARCA),
                        ft.Divider(height=1, color=ConfigSistema.BEGE_MARCA),
                        ft.ResponsiveRow([
                            ft.Container(content=self.nome_field, col={"sm": 12, "md": 7}),
                            ft.Container(content=self.cpf_field, col={"sm": 12, "md": 5}),
                        ], spacing=10),
                        
                        ft.Container(height=20),
                        
                        # Procedimentos Disponíveis
                        ft.Text("PROCEDIMENTOS DISPONÍVEIS", size=16, weight=ft.FontWeight.BOLD, color=ConfigSistema.AZUL_MARCA),
                        ft.Divider(height=1, color=ConfigSistema.BEGE_MARCA),
                        
                        ft.ResponsiveRow([
                            ft.Container(content=self.busca_field, col={"sm": 12, "md": 6}),
                            ft.Container(content=self.novo_procedimento_field, col={"sm": 12, "md": 5}),
                            ft.Container(
                                content=ft.ElevatedButton(
                                    "+", on_click=self._adicionar_novo_procedimento,
                                    bgcolor=ft.Colors.with_opacity(0.15, "#059669"), 
                                    color="#059669",
                                    height=45, width=60, tooltip="Adicionar Procedimento",
                                    style=ft.ButtonStyle(
                                        text_style=ft.TextStyle(size=18, weight=ft.FontWeight.BOLD),
                                        shape=ft.RoundedRectangleBorder(radius=6),
                                        side=ft.BorderSide(1.5, ft.Colors.with_opacity(0.6, "#059669")),
                                        shadow_color=ft.Colors.with_opacity(0.2, "#059669"),
                                        elevation=5,
                                    )
                                ),
                                col={"sm": 12, "md": 1}, alignment=ft.alignment.center,
                            )
                        ], spacing=8),
                        
                        ft.Container(height=8),
                        
                        ft.Container(
                            content=self.lista_procedimentos,
                            border=ft.border.all(1.5, ft.Colors.with_opacity(0.3, ConfigSistema.BEGE_MARCA)),
                            border_radius=10, padding=10, bgcolor=ConfigSistema.BRANCO,
                        ),
                    ], spacing=8),
                    padding=15, 
                    bgcolor=ConfigSistema.BRANCO,
                    border_radius=15,
                    border=ft.border.all(1.5, ft.Colors.with_opacity(0.3, ConfigSistema.BEGE_MARCA)),
                    shadow=ft.BoxShadow(
                        spread_radius=0,
                        blur_radius=15,
                        color=ft.Colors.with_opacity(0.15, ConfigSistema.AZUL_MARCA),
                        offset=ft.Offset(0, 5),
                    ),
                    col={"sm": 12, "md": 6},
                ),
                
                # CARD DIREITO
                ft.Container(
                    content=ft.Column([
                        # Tipo de Exame
                        ft.Text("TIPO DE EXAME", size=16, weight=ft.FontWeight.BOLD, color=ConfigSistema.AZUL_MARCA),
                        ft.Divider(height=1, color=ConfigSistema.BEGE_MARCA),
                        ft.Container(height=8),
                        self.tipo_exame_dropdown.container,
                        
                        ft.Container(height=20),
                        
                        # Procedimentos Selecionados
                        ft.Text("PROCEDIMENTOS SELECIONADOS", size=16, weight=ft.FontWeight.BOLD, color=ConfigSistema.AZUL_MARCA),
                        ft.Divider(height=1, color=ConfigSistema.BEGE_MARCA),
                        
                        ft.Container(
                            content=self.lista_selecionados,
                            border=ft.border.all(1.5, ft.Colors.with_opacity(0.3, ConfigSistema.BEGE_MARCA)),
                            border_radius=10, padding=10, bgcolor=ConfigSistema.BRANCO, height=350,
                        ),

                        
                        # BOTÕES DE AÇÃO - 4 BOTÕES EM LINHA
                        ft.Container(
                            content=ft.Row([
                                ft.ElevatedButton(
                                    "Puxar Favoritos", 
                                    icon=ft.Icons.STAR,
                                    on_click=self._adicionar_obrigatorios,
                                    bgcolor=ft.Colors.with_opacity(0.15, "#FFD700"), 
                                    color="#333333", 
                                    height=48, 
                                    expand=True,
                                    style=ft.ButtonStyle(
                                        text_style=ft.TextStyle(size=14, weight=ft.FontWeight.W_600),
                                        shape=ft.RoundedRectangleBorder(radius=6),
                                        side=ft.BorderSide(1.5, ft.Colors.with_opacity(0.6, "#FFD700")),
                                        shadow_color=ft.Colors.with_opacity(0.3, "#FFD700"),
                                        elevation=5,
                                    )
                                ),
                                ft.Container(width=4),
                                ft.ElevatedButton(
                                    "Limpar Procedimentos", 
                                    icon=ft.Icons.CLEAR,
                                    on_click=self._limpar_procedimentos,
                                    bgcolor=ft.Colors.with_opacity(0.15, "#ff7043"), 
                                    color="#333333", 
                                    height=48, 
                                    expand=True,
                                    style=ft.ButtonStyle(
                                        text_style=ft.TextStyle(size=12, weight=ft.FontWeight.W_600),
                                        shape=ft.RoundedRectangleBorder(radius=6),
                                        side=ft.BorderSide(1.5, ft.Colors.with_opacity(0.6, "#ff7043")),
                                        shadow_color=ft.Colors.with_opacity(0.3, "#ff7043"),
                                        elevation=5,
                                    )
                                ),
                                ft.Container(width=4),
                                ft.ElevatedButton(
                                    "Limpar Tudo", 
                                    icon=ft.Icons.CLEAR_ALL,
                                    on_click=self._limpar_tudo,
                                    bgcolor=ft.Colors.with_opacity(0.15, ConfigSistema.CINZA_ESCURO), 
                                    color="#333333", 
                                    height=48, 
                                    expand=True,
                                    style=ft.ButtonStyle(
                                        text_style=ft.TextStyle(size=14, weight=ft.FontWeight.W_600),
                                        shape=ft.RoundedRectangleBorder(radius=6),
                                        side=ft.BorderSide(1.5, ft.Colors.with_opacity(0.6, ConfigSistema.CINZA_ESCURO)),
                                        shadow_color=ft.Colors.with_opacity(0.3, ConfigSistema.CINZA_ESCURO),
                                        elevation=5,
                                    )
                                ),
                                ft.Container(width=4),
                                ft.ElevatedButton(
                                    "Imprimir", 
                                    icon=ft.Icons.PRINT,
                                    on_click=self._gerar_checklist,
                                    bgcolor=ft.Colors.with_opacity(0.15, ConfigSistema.AZUL_MARCA), 
                                    color="#333333", 
                                    height=48, 
                                    expand=True,
                                    style=ft.ButtonStyle(
                                        text_style=ft.TextStyle(size=14, weight=ft.FontWeight.W_600),
                                        shape=ft.RoundedRectangleBorder(radius=6),
                                        side=ft.BorderSide(1.5, ft.Colors.with_opacity(0.6, ConfigSistema.AZUL_MARCA)),
                                        shadow_color=ft.Colors.with_opacity(0.3, ConfigSistema.AZUL_MARCA),
                                        elevation=5,
                                    )
                                ),
                            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN, spacing=0),
                            padding=ft.padding.symmetric(horizontal=2, vertical=8),
                        ),
                    ], spacing=8),
                    padding=15, 
                    bgcolor=ConfigSistema.BRANCO,
                    border_radius=15,
                    border=ft.border.all(1.5, ft.Colors.with_opacity(0.3, ConfigSistema.BEGE_MARCA)),
                    shadow=ft.BoxShadow(
                        spread_radius=0,
                        blur_radius=15,
                        color=ft.Colors.with_opacity(0.15, ConfigSistema.AZUL_MARCA),
                        offset=ft.Offset(0, 5),
                    ),
                    col={"sm": 12, "md": 6},
                ),
            ], spacing=20),
            
            # Rodapé
            ft.Container(
                content=ft.Text(
                    "LaborePlus © 2025 - Dr. Murillo A. Lopes",
                    size=11, color=ConfigSistema.CINZA_ESCURO, text_align=ft.TextAlign.CENTER,
                ),
                alignment=ft.alignment.center, padding=8, bgcolor=ConfigSistema.CINZA_CLARO,
                margin=ft.margin.only(top=10), border_radius=6,
            )
        ])
# =================== TESTES UNITÁRIOS ===================

class TestSistemaClinico(unittest.TestCase):
    """Testes unitários para a classe SistemaClinico"""
    
    def setUp(self):
        """Configuração inicial para cada teste"""
        self.sistema = SistemaClinico()
    
    def test_validar_cpf_valido(self):
        """Testa validação de CPF válido"""
        cpf_valido = "12345678909"
        self.assertTrue(self.sistema.validar_cpf(cpf_valido))
    
    def test_validar_cpf_invalido(self):
        """Testa validação de CPF inválido"""
        cpfs_invalidos = ["11111111111", "123456789", "123.456.789-00"]
        for cpf in cpfs_invalidos:
            with self.subTest(cpf=cpf):
                self.assertFalse(self.sistema.validar_cpf(cpf))
    
    def test_formatar_cpf(self):
        """Testa formatação de CPF"""
        casos = [
            ("12345678909", "123.456.789-09"),
            ("123456789", "123.456.789"),
            ("123456", "123.456"),
            ("123", "123")
        ]
        for entrada, esperado in casos:
            with self.subTest(entrada=entrada):
                self.assertEqual(self.sistema.formatar_cpf(entrada), esperado)
    
    def test_adicionar_procedimento(self):
        """Testa adição de procedimento"""
        novo_proc = "Teste Procedimento"
        resultado = self.sistema.adicionar_procedimento(novo_proc)
        self.assertTrue(resultado)
        self.assertIn(novo_proc, self.sistema.procedimentos_db)
    
    def test_adicionar_procedimento_duplicado(self):
        """Testa que não permite adicionar procedimento duplicado"""
        proc_existente = self.sistema.procedimentos_db[0]
        resultado = self.sistema.adicionar_procedimento(proc_existente)
        self.assertFalse(resultado)
    
    def test_alternar_obrigatorio(self):
        """Testa alternância de procedimento obrigatório"""
        procedimento = "Teste Obrigatório"
        self.sistema.adicionar_procedimento(procedimento)
        
        # Tornar obrigatório
        self.sistema.alternar_obrigatorio(procedimento)
        self.assertIn(procedimento, self.sistema.procedimentos_obrigatorios)
        
        # Remover obrigatório
        self.sistema.alternar_obrigatorio(procedimento)
        self.assertNotIn(procedimento, self.sistema.procedimentos_obrigatorios)

class TestGerenciadorHistorico(unittest.TestCase):
    """Testes unitários para o GerenciadorHistorico"""
    
    def setUp(self):
        """Configuração inicial para cada teste"""
        self.historico = GerenciadorHistorico()
        # Limpar histórico para testes
        self.historico.historico = []
    
    def test_adicionar_checklist(self):
        """Testa adição de checklist ao histórico"""
        checklist_id = self.historico.adicionar_checklist(
            "João Silva", "123.456.789-09", "Admissional", 
            ["Exame Clínico"], "teste.pdf"
        )
        
        self.assertEqual(checklist_id, 1)
        self.assertEqual(len(self.historico.historico), 1)
        self.assertEqual(self.historico.historico[0]['nome'], "João Silva")
    
    def test_buscar_por_funcionario(self):
        """Testa busca por nome de funcionário"""
        self.historico.adicionar_checklist(
            "João Silva", "123.456.789-09", "Admissional", 
            ["Exame Clínico"], "teste1.pdf"
        )
        self.historico.adicionar_checklist(
            "Maria Santos", "987.654.321-00", "Periódico", 
            ["Exame Clínico"], "teste2.pdf"
        )
        
        resultados = self.historico.buscar_por_funcionario("João")
        self.assertEqual(len(resultados), 1)
        self.assertEqual(resultados[0]['nome'], "João Silva")
    
    def test_buscar_por_cpf(self):
        """Testa busca por CPF"""
        self.historico.adicionar_checklist(
            "João Silva", "123.456.789-09", "Admissional", 
            ["Exame Clínico"], "teste1.pdf"
        )
        
        resultados = self.historico.buscar_por_cpf("123.456.789-09")
        self.assertEqual(len(resultados), 1)
        self.assertEqual(resultados[0]['cpf'], "123.456.789-09")

class TestTipoExameModerno(unittest.TestCase):
    """Testes unitários para TipoExameModerno"""
    
    def setUp(self):
        """Configuração inicial para cada teste"""
        self.mock_page = Mock()
        self.tipo_exame = TipoExameModerno(
            self.mock_page, "#00365f", "#ffffff", "#374151", "#f3f4f6"
        )
    
    def test_valor_inicial(self):
        """Testa valor inicial selecionado"""
        self.assertEqual(self.tipo_exame.value, "Admissional")

# =================== FUNÇÃO MAIN E EXECUÇÃO ===================

def main(page: ft.Page):
    """Função principal simplificada - apenas inicializa o gerenciador"""
    # Forçar tema claro ANTES de criar a interface
    page.theme_mode = ft.ThemeMode.LIGHT
    
    # Definir ícone da janela/barra de tarefas - OPÇÃO 2
    try:
        import sys
        import os
        
        # Detectar se está rodando como executável
        if getattr(sys, 'frozen', False):
            # Rodando como executável
            icon_path = os.path.join(sys._MEIPASS, "LaborePlus_Símbolo.ico")
        else:
            # Rodando como script Python
            icon_path = "LaborePlus_Símbolo.ico"
        
        page.window.icon = icon_path
    except Exception as e:
        print(f"Não foi possível carregar o ícone: {e}")
        pass  # Se não encontrar o ícone, continua sem erro
    
    page.update()
    
    gerenciador = GerenciadorInterface(page)
    page.add(gerenciador.construir_interface())


def executar_testes():
    """Executa todos os testes unitários"""
    import sys
    
    # Criar suite de testes
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Adicionar classes de teste
    suite.addTests(loader.loadTestsFromTestCase(TestSistemaClinico))
    suite.addTests(loader.loadTestsFromTestCase(TestGerenciadorHistorico))
    suite.addTests(loader.loadTestsFromTestCase(TestTipoExameModerno))
    
    # Executar testes
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Retornar se todos os testes passaram
    return result.wasSuccessful()

if __name__ == "__main__":
    import sys
    
    # Verificar se deve executar testes
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        if executar_testes():
            print("✅ Todos os testes passaram!")
        else:
            print("❌ Alguns testes falharam!")
        sys.exit()
    
    # Instalar dependências silenciosamente
    try:
        import reportlab
    except ImportError:
        subprocess.check_call(["pip", "install", "reportlab"])
    
    # Executar aplicação
    ft.app(target=main)