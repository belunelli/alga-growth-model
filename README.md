# Modelo de Crescimento de Chlorella vulgaris

Implementação simples e educacional do modelo matemático de crescimento de *Chlorella vulgaris* baseado em Chang et al. (2016).

## 📚 O Projeto

Este repositório contém um **modelo monolítico de simulação** que implementa um modelo logístico de Verhulst modificado considerando os efeitos acoplados de:
- **Intensidade luminosa** (I, μmol/m²/s)
- **Carbono inorgânico dissolvido** (DIC, mM)

Ideal para aprender a implementar modelos matemáticos em Python de forma simples e didática.

## 🚀 Início Rápido

### Instalação

```bash
# Clonar repositório
git clone https://github.com/seu-usuario/algae-growth-model.git
cd algae-growth-model

# Instalar dependências
pip install -r requirements.txt
```

### Uso Básico (3 linhas)

```python
from alga_growth_model import simulate

t, X = simulate(I=120, DIC=17.09)  # Condições ótimas
print(f"Biomassa final: {X[-1]:.3f} g/L")  # 2.151 g/L
```

### Com Gráfico

```python
from alga_growth_model import simulate, plot_growth

t, X = simulate(I=120, DIC=17.09)
plot_growth(t, X, I=120, DIC=17.09, filename="growth.png", show=False)
```

### Executar Simulações Completas

```bash
python alga_growth_model.py
```

Gera 3 gráficos PNG com simulações em diferentes condições.

## 📁 Estrutura

```
algae-growth-model/
├── alga_growth_model.py    # Arquivo principal (simulação + plotagem)
├── CLAUDE.md               # Documentação técnica detalhada
├── requirements.txt        # Dependências
├── README.md              # Este arquivo
├── LICENSE                # Licença MIT
└── docs/                  # Referência (paper original)
```

## 🧪 Funcionalidades

### Simulação
- `simulate(I, DIC, t_max, n_points)` - Simula crescimento usando ODE solver

### Cálculos
- `calc_Xmax(I, DIC)` - Equação 12 (Capacidade máxima de biomassa)
- `calc_mu_max(I, DIC)` - Equação 13 (Taxa máxima de crescimento)
- `calc_co2_biofixation(t, X)` - Equação 14 (Biofixação de CO₂)

### Visualização
- `plot_growth(t, X, I, DIC)` - Plota crescimento

## 📊 Equações Implementadas

O modelo implementa 4 equações principais de Chang et al. (2016):

1. **Eq. 12** - Capacidade máxima de biomassa:
   ```
   Xmax = a1 × Xopt × exp(-b1×((I/I_opt1)-1)²) × exp(-c1×((DIC/DIC_opt1)-1)²)
   ```

2. **Eq. 13** - Taxa específica máxima de crescimento:
   ```
   μmax = a2 × μopt × exp(-b2×((I/I_opt2)-1)²) × exp(-c2×((DIC/DIC_opt2)-1)²)
   ```

3. **Eq. 2** - Taxa específica de crescimento (Logística):
   ```
   μ = μmax × (1 - X/Xmax)
   ```

4. **EDO Principal**:
   ```
   dX/dt = μ × X
   ```

5. **Eq. 14** - Biofixação de CO₂:
   ```
   qCO₂ = (Cc/100) × (MCO₂/MC) × dX/dt
   ```

## 🔧 Dependências

- **numpy** ≥ 1.21.0 - Operações numéricas
- **scipy** ≥ 1.7.0 - ODE solver (odeint)
- **matplotlib** ≥ 3.5.0 - Plotagem

## 📖 Documentação

Para detalhes técnicos completos, veja [CLAUDE.md](CLAUDE.md):
- Arquitetura do código
- Modificação de parâmetros
- Exemplos avançados
- Troubleshooting

## 📚 Referência

Chang, H. X., Huang, Y., Fu, Q., Liao, Q., & Zhu, X. (2016). Kinetic characteristics and modeling of microalgae Chlorella vulgaris growth and CO2 biofixation considering the coupled effects of light intensity and dissolved inorganic carbon. *Bioresource Technology*, 206, 231-238.

**DOI:** [10.1016/j.biortech.2016.01.087](https://doi.org/10.1016/j.biortech.2016.01.087)

## 📝 Licença

Este projeto está licenciado sob a Licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes.

## 🎯 Objetivo Educacional

Este código foi desenvolvido como ferramenta de aprendizado para:
- Entender modelos matemáticos de crescimento microbiano
- Aprender a implementar ODEs em Python
- Validar resultados de simulação com dados reais
- Explorar sensibilidade a parâmetros

**Perfeito para:**
- Alunos de Biologia/Biotecnologia
- Aulas de Modelagem Matemática
- Projetos de Pesquisa
- Referência de implementação

---

**Autor:** Baseado em implementação para fins educacionais
**Versão:** 1.0
**Status:** Pronto para uso
