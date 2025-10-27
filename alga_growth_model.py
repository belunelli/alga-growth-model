#!/usr/bin/env python3
"""
MODELO MONOLÍTICO DE CRESCIMENTO DE CHLORELLA VULGARIS
========================================================

Implementação simples do modelo matemático de crescimento e biofixação de CO₂
para Chlorella vulgaris baseado em Chang et al. (2016).

Baseado em: Chang, H. X., Huang, Y., Fu, Q., Liao, Q., & Zhu, X. (2016)
            Kinetic characteristics and modeling of microalgae Chlorella vulgaris
            growth and CO2 biofixation considering the coupled effects of light
            intensity and dissolved inorganic carbon.
            Bioresource Technology, 206, 231-238
            DOI: 10.1016/j.biortech.2016.01.087

ESTRUTURA:
  - Seção 1: PARÂMETROS (linha 30)
  - Seção 2: FUNÇÕES DO MODELO (linha 120)
  - Seção 3: FUNÇÕES DE PLOTAGEM (linha 280)
  - Seção 4: FUNÇÃO PRINCIPAL (linha 400)

USO RÁPIDO:
    # Simulação básica
    t, X = simulate(I=120, DIC=17.09)
    print(f"Biomassa final: {X[-1]:.3f} g/L")

    # Com gráfico
    plot_growth(t, X, I=120, DIC=17.09)

    # Análises completas
    main()  # Executa tudo
"""

import numpy as np
from scipy.integrate import odeint
import matplotlib.pyplot as plt
from pathlib import Path


# =============================================================================
# SEÇÃO 1: PARÂMETROS DO MODELO
# =============================================================================
# TODOS OS PARÂMETROS ESTÃO DEFINIDOS AQUI - FÁCIL MODIFICAÇÃO
# Edite estes dicionários para customizar o modelo
# =============================================================================

# PARÂMETROS BIOLÓGICOS (Tabela 2 do artigo Chang et al. 2016)
PARAMS_BIOLOGIA = {
    # Valores ótimos experimentais
    'Xopt': 2.303,              # g/L - concentração máxima de biomassa
    'mu_opt': 0.078,            # h⁻¹ - taxa específica máxima de crescimento

    # Intensidades luminosas ótimas (μmol/m²/s)
    'I_opt_1': 120.0,           # Ótimo para Xmax
    'I_opt_2': 120.0,           # Ótimo para μmax

    # Concentrações DIC ótimas (mM)
    'DIC_opt_1': 17.09,         # Ótimo para Xmax
    'DIC_opt_2': 16.78,         # Ótimo para μmax

    # Coeficientes gaussianos do modelo
    'a1': 0.934,                # Fator de correção para Xopt
    'a2': 0.961,                # Fator de correção para μopt
    'b1': 0.505,                # Coeficiente de luz para Xmax
    'b2': 0.384,                # Coeficiente de luz para μmax
    'c1': 2.538,                # Coeficiente DIC para Xmax
    'c2': 3.071,                # Coeficiente DIC para μmax

    # Constantes para biofixação de CO₂
    'Cc': 51.93,                # % - conteúdo de carbono celular
    'MCO2': 44.01,              # g/mol - massa molar CO₂
    'MC': 12.01,                # g/mol - massa molar carbono

    # Condição inicial
    'X0': 0.0157,               # g/L - biomassa inicial
}

# PARÂMETROS DE SIMULAÇÃO
PARAMS_SIMULACAO = {
    't_max': 200,               # Horas - tempo máximo de simulação
    'n_points': 200,            # Número de pontos da simulação
}

# PARÂMETROS DE PLOTAGEM
PARAMS_PLOTAGEM = {
    'figsize_single': (10, 6),  # Tamanho de figura única
    'dpi': 300,                 # Resolução das imagens
    'linewidth_model': 2.5,     # Largura linha do modelo
    'fontsize_title': 14,       # Tamanho fonte título
    'fontsize_label': 12,       # Tamanho fonte labels
}

# CONFIGURAÇÕES DE DIRETÓRIOS DE SAÍDA
PARAMS_DADOS = {
    'dir_output': 'data/output',
}


# =============================================================================
# SEÇÃO 2: FUNÇÕES DO MODELO (Equações de Chang et al. 2016)
# =============================================================================

def calc_Xmax(I, DIC, params=PARAMS_BIOLOGIA):
    """
    Calcula a capacidade máxima de biomassa (Eq. 12).

    Fórmula:
        Xmax = a1 × Xopt × exp(-b1×((I/I_opt1)-1)²) × exp(-c1×((DIC/DIC_opt1)-1)²)

    Interpretação:
        - Xopt: capacidade máxima em condições ótimas
        - Termo de luz: gaussiana centrada em I_opt1
        - Termo de DIC: gaussiana centrada em DIC_opt1
        - Se I e DIC se afastam dos ótimos, Xmax diminui

    Args:
        I: Intensidade luminosa (μmol/m²/s), range válido: 50-300
        DIC: Concentração de carbono inorgânico dissolvido (mM), range: 7-30
        params: Dicionário com parâmetros do modelo

    Returns:
        Xmax em g/L (concentração máxima de biomassa)

    Exemplo:
        >>> Xmax = calc_Xmax(I=120, DIC=17.09)  # Condições ótimas
        >>> print(f"Xmax = {Xmax:.3f} g/L")
    """
    # Calcula desvios dos valores ótimos
    I_dev = (I / params['I_opt_1']) - 1.0
    DIC_dev = (DIC / params['DIC_opt_1']) - 1.0

    # Termos gaussianos (quanto mais perto do ótimo, mais próximo de 1)
    light_term = np.exp(-params['b1'] * I_dev**2)
    dic_term = np.exp(-params['c1'] * DIC_dev**2)

    # Eq. 12
    Xmax = params['a1'] * params['Xopt'] * light_term * dic_term

    return Xmax


def calc_mu_max(I, DIC, params=PARAMS_BIOLOGIA):
    """
    Calcula a taxa específica máxima de crescimento (Eq. 13).

    Fórmula:
        μmax = a2 × μopt × exp(-b2×((I/I_opt2)-1)²) × exp(-c2×((DIC/DIC_opt2)-1)²)

    Interpretação:
        - μopt: taxa máxima em condições ótimas
        - Mesmo padrão gaussiano de Xmax
        - Nota: I_opt_2 e DIC_opt_2 podem diferir de I_opt_1 e DIC_opt_1

    Args:
        I: Intensidade luminosa (μmol/m²/s)
        DIC: Concentração DIC (mM)
        params: Dicionário com parâmetros

    Returns:
        μmax em h⁻¹ (taxa específica de crescimento máxima)
    """
    # Calcula desvios
    I_dev = (I / params['I_opt_2']) - 1.0
    DIC_dev = (DIC / params['DIC_opt_2']) - 1.0

    # Termos gaussianos
    light_term = np.exp(-params['b2'] * I_dev**2)
    dic_term = np.exp(-params['c2'] * DIC_dev**2)

    # Eq. 13
    mu_max = params['a2'] * params['mu_opt'] * light_term * dic_term

    return mu_max


def simulate(I, DIC, t_max=None, n_points=None, params=PARAMS_BIOLOGIA,
             params_sim=PARAMS_SIMULACAO):
    """
    Simula o crescimento de Chlorella vulgaris.

    Integra numericamente a Equação Diferencial Ordinária (EDO):
        dX/dt = μ × X

    Onde:
        μ = μmax × (1 - X/Xmax)  [Eq. 2 - Modelo Logístico de Verhulst]

    Processo:
        1. Calcula Xmax e μmax para as condições (I, DIC)
        2. Define a EDO da taxa de crescimento
        3. Integra usando scipy.odeint (método de Runge-Kutta adaptativo)
        4. Retorna série temporal de biomassa

    Args:
        I: Intensidade luminosa (μmol/m²/s), ex: 120
        DIC: Concentração DIC (mM), ex: 17.09
        t_max: Tempo máximo (h), default do PARAMS_SIMULACAO
        n_points: Número de pontos, default do PARAMS_SIMULACAO
        params: Parâmetros biológicos (dict)
        params_sim: Parâmetros de simulação (dict)

    Returns:
        t: Array de tempos (h)
        X: Array de concentração de biomassa (g/L)

    Exemplo:
        >>> t, X = simulate(I=120, DIC=17.09)
        >>> print(f"Tempo final: {t[-1]:.1f} h")
        >>> print(f"Biomassa final: {X[-1]:.3f} g/L")
    """
    # Usa default se não especificado
    if t_max is None:
        t_max = params_sim['t_max']
    if n_points is None:
        n_points = params_sim['n_points']

    # Calcula parâmetros para as condições experimentais dadas
    Xmax = calc_Xmax(I, DIC, params)
    mu_max = calc_mu_max(I, DIC, params)

    # Define a Equação Diferencial: dX/dt = μ × X
    def ode(X, t):
        """
        Função da EDO para scipy.odeint

        X: Concentração de biomassa (g/L)
        t: Tempo (h)

        Retorna dX/dt (taxa de mudança da biomassa)
        """
        # Evita valores negativos/muito pequenos
        X_safe = max(X[0], 1e-10)

        # Eq. 2: Taxa específica de crescimento (modelo logístico)
        mu = mu_max * (1 - X_safe / Xmax)

        # EDO: dX/dt = μ × X
        dX_dt = mu * X_safe

        return [dX_dt]

    # Cria array de tempos
    t = np.linspace(0, t_max, n_points)

    # Integração numérica usando odeint (Runge-Kutta adaptativo)
    X = odeint(ode, [params['X0']], t)[:, 0]

    return t, X


def calc_co2_biofixation(t, X, params=PARAMS_BIOLOGIA):
    """
    Calcula a taxa e total de CO₂ biofixado (Eq. 14).

    Fórmula:
        qCO₂ = (Cc/100) × (MCO₂/MC) × dX/dt

    Onde:
        - Cc: Conteúdo de carbono celular (%)
        - MCO₂: Massa molar do CO₂ (44.01 g/mol)
        - MC: Massa molar do C (12.01 g/mol)
        - dX/dt: Taxa de crescimento da biomassa

    Args:
        t: Array de tempos (h)
        X: Array de biomassa (g/L)
        params: Parâmetros com Cc, MCO2, MC

    Returns:
        co2_rate: Taxa de biofixação (g CO₂/L/h) - array
        co2_cumulative: CO₂ total acumulado (g CO₂/L) - array
    """
    # Calcula dX/dt por diferenças finitas (gradiente)
    dX_dt = np.gradient(X, t)

    # Eq. 14: taxa de biofixação de CO₂
    co2_rate = (params['Cc'] / 100.0) * (params['MCO2'] / params['MC']) * dX_dt

    # Integra para obter acumulado (usando regra trapezoidal)
    co2_cumulative = np.cumsum(co2_rate * np.gradient(t))

    return co2_rate, co2_cumulative


# =============================================================================
# SEÇÃO 3: FUNÇÕES DE PLOTAGEM
# =============================================================================

def plot_growth(t, X, I=None, DIC=None, filename=None, show=True,
               params_plot=PARAMS_PLOTAGEM):
    """
    Plota uma curva de crescimento.

    Visualização simples: tempo vs biomassa com grid e legenda.

    Args:
        t: Array de tempos (h)
        X: Array de biomassa (g/L)
        I: Intensidade luminosa (opcional, aparece no título)
        DIC: Concentração DIC (opcional, aparece no título)
        filename: Caminho para salvar (ex: "data/output/growth.png")
        show: Se True, mostra o gráfico; se False, apenas salva
        params_plot: Dicionário com configurações de plotagem

    Returns:
        None (salva arquivo e/ou mostra gráfico)

    Exemplo:
        >>> t, X = simulate(I=120, DIC=17.09)
        >>> plot_growth(t, X, I=120, DIC=17.09,
        ...            filename='data/output/growth.png', show=False)
    """
    fig, ax = plt.subplots(figsize=params_plot['figsize_single'])

    # Plot da curva de crescimento
    ax.plot(t, X, 'b-', linewidth=params_plot['linewidth_model'],
            label='Biomassa', alpha=0.8)

    # Labels e título
    ax.set_xlabel('Tempo (h)', fontsize=params_plot['fontsize_label'],
                  fontweight='bold')
    ax.set_ylabel('Concentração de Biomassa (g/L)',
                  fontsize=params_plot['fontsize_label'], fontweight='bold')

    # Título com condições
    if I is not None and DIC is not None:
        title = f'Crescimento Chlorella vulgaris - I={I} μmol/m²/s, DIC={DIC:.2f} mM'
    else:
        title = 'Crescimento Chlorella vulgaris'
    ax.set_title(title, fontsize=params_plot['fontsize_title'], fontweight='bold')

    # Formatação
    ax.grid(True, alpha=0.3, linestyle='--')
    ax.legend(fontsize=11)

    plt.tight_layout()

    # Salva se especificado
    if filename:
        Path(filename).parent.mkdir(parents=True, exist_ok=True)
        plt.savefig(filename, dpi=params_plot['dpi'], bbox_inches='tight')

    # Mostra se solicitado
    if show:
        plt.show()
    else:
        plt.close()


# =============================================================================
# SEÇÃO 4: FUNÇÃO PRINCIPAL (MAIN)
# =============================================================================

def main():
    """
    Executa pipeline simples de simulações de crescimento:

    1. Simula crescimento em condições ótimas
    2. Simula crescimento em condições subótimas
    3. Calcula parâmetros e biofixação de CO₂
    4. Gera gráficos em data/output/
    """

    # Cria diretório de saída
    output_dir = Path(PARAMS_DADOS['dir_output'])
    output_dir.mkdir(parents=True, exist_ok=True)

    print("\n" + "=" * 70)
    print(" MODELO DE CRESCIMENTO DE CHLORELLA VULGARIS")
    print(" Versão Monolítica - Simplificada para Iniciantes")
    print("=" * 70)
    print(" Baseado em: Chang et al. (2016)")
    print("=" * 70)
    print()

    # =========================================================================
    # 1. SIMULAÇÃO EM CONDIÇÕES ÓTIMAS
    # =========================================================================
    print("\n1. SIMULAÇÃO EM CONDIÇÕES ÓTIMAS")
    print("-" * 70)

    I_opt = 120.0
    DIC_opt = 17.09

    print(f"   Intensidade luminosa (I): {I_opt} μmol/m²/s")
    print(f"   Carbono inorgânico (DIC): {DIC_opt} mM")
    print()

    t_opt, X_opt = simulate(I=I_opt, DIC=DIC_opt)
    Xmax_opt = calc_Xmax(I_opt, DIC_opt)
    mu_max_opt = calc_mu_max(I_opt, DIC_opt)
    co2_rate, co2_cum = calc_co2_biofixation(t_opt, X_opt)

    print(f"   Resultados:")
    print(f"   - Xmax (capacidade máxima):    {Xmax_opt:.3f} g/L")
    print(f"   - μmax (taxa máx. crescimento): {mu_max_opt:.4f} h⁻¹")
    print(f"   - Biomassa inicial:            {X_opt[0]:.4f} g/L")
    print(f"   - Biomassa final (t={t_opt[-1]:.0f}h):       {X_opt[-1]:.3f} g/L")
    print(f"   - CO₂ total fixado:            {co2_cum[-1]:.3f} g CO₂/L")
    print(f"   - Taxa máx. CO₂:               {np.max(co2_rate):.4f} g CO₂/L/h")

    plot_growth(t_opt, X_opt, I=I_opt, DIC=DIC_opt,
               filename=str(output_dir / "01_optimal_conditions.png"),
               show=False)
    print(f"\n   ✓ Gráfico salvo: {output_dir}/01_optimal_conditions.png")

    # =========================================================================
    # 2. SIMULAÇÃO EM CONDIÇÕES SUBÓTIMAS
    # =========================================================================
    print("\n\n2. SIMULAÇÃO EM CONDIÇÕES SUBÓTIMAS")
    print("-" * 70)

    I_sub = 80.0
    DIC_sub = 10.0

    print(f"   Intensidade luminosa (I): {I_sub} μmol/m²/s")
    print(f"   Carbono inorgânico (DIC): {DIC_sub} mM")
    print()

    t_sub, X_sub = simulate(I=I_sub, DIC=DIC_sub)
    Xmax_sub = calc_Xmax(I_sub, DIC_sub)
    mu_max_sub = calc_mu_max(I_sub, DIC_sub)

    print(f"   Resultados:")
    print(f"   - Xmax (capacidade máxima):    {Xmax_sub:.3f} g/L")
    print(f"   - μmax (taxa máx. crescimento): {mu_max_sub:.4f} h⁻¹")
    print(f"   - Biomassa final (t={t_sub[-1]:.0f}h):       {X_sub[-1]:.3f} g/L")

    plot_growth(t_sub, X_sub, I=I_sub, DIC=DIC_sub,
               filename=str(output_dir / "02_suboptimal_conditions.png"),
               show=False)
    print(f"\n   ✓ Gráfico salvo: {output_dir}/02_suboptimal_conditions.png")

    # =========================================================================
    # 3. COMPARAÇÃO ÓTIMAS vs SUBÓTIMAS
    # =========================================================================
    print("\n\n3. COMPARAÇÃO: ÓTIMAS vs SUBÓTIMAS")
    print("-" * 70)

    improvement_Xmax = ((Xmax_opt - Xmax_sub) / Xmax_sub) * 100
    improvement_mu = ((mu_max_opt - mu_max_sub) / mu_max_sub) * 100
    improvement_biomass = ((X_opt[-1] - X_sub[-1]) / X_sub[-1]) * 100

    print(f"   Melhoria em condições ótimas:")
    print(f"   - Xmax:       +{improvement_Xmax:.1f}%")
    print(f"   - μmax:       +{improvement_mu:.1f}%")
    print(f"   - Biomassa:   +{improvement_biomass:.1f}%")

    # =========================================================================
    # 4. SIMULAÇÃO EM RANGE DE CONDIÇÕES
    # =========================================================================
    print("\n\n4. SIMULAÇÕES ADICIONAIS")
    print("-" * 70)

    # Define range de condições
    I_values = [50, 100, 150, 200, 250, 300]
    DIC_values = [10, 15, 20, 25]

    print(f"   Simulando {len(I_values)} × {len(DIC_values)} = {len(I_values)*len(DIC_values)} combinações...")

    # Cria figura com gráficos de contorno
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    axes = axes.flatten()

    # Plota alguns exemplos
    examples = [
        (50, 10, 0, "I=50, DIC=10 (Baixa)"),
        (120, 17, 1, "I=120, DIC=17 (Ótima)"),
        (200, 25, 2, "I=200, DIC=25 (Alta)"),
        (300, 10, 3, "I=300, DIC=10 (Extrema)"),
    ]

    for I, DIC, ax_idx, label in examples:
        ax = axes[ax_idx]
        t_sim, X_sim = simulate(I, DIC)
        Xmax_sim = calc_Xmax(I, DIC)

        ax.plot(t_sim, X_sim, 'b-', linewidth=2.5, label='Modelo')
        ax.axhline(Xmax_sim, color='r', linestyle='--', alpha=0.5, label=f'Xmax={Xmax_sim:.3f}')

        ax.set_xlabel('Tempo (h)', fontsize=11, fontweight='bold')
        ax.set_ylabel('Biomassa (g/L)', fontsize=11, fontweight='bold')
        ax.set_title(f'{label}', fontsize=12, fontweight='bold')
        ax.grid(True, alpha=0.3)
        ax.legend(fontsize=10)

    plt.tight_layout()
    plt.savefig(str(output_dir / "03_parameter_exploration.png"),
               dpi=PARAMS_PLOTAGEM['dpi'], bbox_inches='tight')
    print(f"   ✓ Gráfico salvo: {output_dir}/03_parameter_exploration.png")
    plt.close()

    # =========================================================================
    # CONCLUSÃO
    # =========================================================================
    print("\n" + "=" * 70)
    print(" ✓ SIMULAÇÃO CONCLUÍDA COM SUCESSO!")
    print("=" * 70)
    print(f" Todos os gráficos foram salvos em:")
    print(f" {output_dir.absolute()}")
    print("=" * 70)
    print()


# =============================================================================
# SCRIPT DE EXECUÇÃO
# =============================================================================

if __name__ == '__main__':
    main()
