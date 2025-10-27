# Contribuindo para o Projeto

Obrigado por seu interesse em contribuir! Este projeto foi criado para fins educacionais.

## 🎓 Como Contribuir

### 1. Reportar Problemas (Issues)
Se encontrar um bug ou tiver uma sugestão, crie uma issue descrevendo:
- O que você tentou fazer
- O que aconteceu
- O que deveria acontecer
- Sua versão de Python e sistema operacional

### 2. Melhorias de Documentação
- Corrija erros de digitação ou esclareça explicações
- Adicione exemplos ou tutoriais
- Melhore a estrutura e clareza

### 3. Novas Funcionalidades
Antes de implementar, abra uma issue descrevendo sua ideia. Algumas diretrizes:

#### Princípios de Design
- **Simplicidade:** Mantenha o código simples e legível
- **Documentação:** Sempre documente funções em português
- **Sem complexidade desnecessária:** Evite OOP avançado, apenas funções
- **Validação:** Teste sua mudança contra o exemplo básico

#### Processo
1. Fork o repositório
2. Crie uma branch: `git checkout -b minha-melhoria`
3. Implemente sua mudança
4. Teste: `python alga_growth_model.py`
5. Commit com mensagem clara: `git commit -m "Descrição da mudança"`
6. Push: `git push origin minha-melhoria`
7. Abra um Pull Request

### 4. Tipos de Contribuição Bem-Vindos

✅ **Bem-vindo:**
- Correções de bugs
- Melhorias de documentação
- Exemplos educacionais
- Otimizações de desempenho
- Testes
- Tradução de comentários

❌ **Não recomendado:**
- Adicionar dependências pesadas
- Refatoração para OOP/design patterns
- Validação experimental (sem dados)
- Mudanças que aumentem significativamente a complexidade

## 📋 Padrões de Código

### Nomeação
```python
# Variáveis e funções em snake_case
t_max = 200
def calc_Xmax(I, DIC):
    pass

# Constantes em UPPER_CASE
PARAMS_BIOLOGIA = {...}
```

### Documentação
```python
def calc_Xmax(I, DIC, params=PARAMS_BIOLOGIA):
    """
    Calcula a capacidade máxima de biomassa (Eq. 12).

    Fórmula:
        Xmax = a1 × Xopt × exp(-b1×((I/I_opt1)-1)²) × ...

    Args:
        I: Intensidade luminosa (μmol/m²/s)
        DIC: Concentração DIC (mM)
        params: Dicionário com parâmetros

    Returns:
        Xmax em g/L
    """
```

### Comentários
```python
# Evite comentários óbvios
X = X + 1  # ❌ Incrementa X

# Prefira comentários que explicam o "porquê"
# Evita valores negativos/muito pequenos na integração
X_safe = max(X[0], 1e-10)  # ✅
```

## 🧪 Testando suas Mudanças

Após implementar, teste:

```bash
# Verifique que o arquivo importa
python -c "from alga_growth_model import *"

# Execute o pipeline completo
python alga_growth_model.py

# Teste uma simulação rápida
python -c "
from alga_growth_model import simulate, calc_Xmax
t, X = simulate(I=120, DIC=17.09)
print(f'Xmax: {calc_Xmax(120, 17.09):.3f} g/L')
print(f'Biomassa: {X[-1]:.3f} g/L')
"
```

## 📝 Commit Messages

Use mensagens claras e descritivas:

```
✅ Bom:
- "Adiciona exemplo de uso com parâmetros customizados"
- "Melhora clareza da documentação de calc_mu_max"
- "Corrige typo em docstring de simulate"

❌ Evite:
- "Fix bug"
- "Update"
- "Changes"
```

## 📚 Referências

- **Paper Original:** Chang et al. (2016) - [DOI:10.1016/j.biortech.2016.01.087](https://doi.org/10.1016/j.biortech.2016.01.087)
- **Documentação:** Veja [CLAUDE.md](CLAUDE.md) para detalhes técnicos
- **Estilo:** Python PEP 8 (com foco em legibilidade)

## ❓ Dúvidas?

Abra uma issue com a tag `[DÚVIDA]` ou entre em contato com o mantenedor.

---

**Obrigado por contribuir!** 🎉
