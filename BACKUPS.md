# BACKUPS — Inventário e restauração

## Backups disponíveis

### Snapshots imutáveis (não rotacionam)

| Arquivo | Data do snapshot | Tamanho | Estado | Localização |
|---------|------------------|---------|--------|-------------|
| `zotero_BEFORE_REORG_2026-05-09.sqlite` | 2026-05-09 20:00 | 23.5 MB | Antes de qualquer mudança nossa | `~/Zotero/_diagnostico/` |
| `zotero_BEFORE_CLEANUP_2026-05-10_1955.sqlite` | 2026-05-10 19:46 | 24.2 MB | Checkpoint entre Scripts A-H | `~/Zotero/_diagnostico/` |

### Auto-rotacionados pelo Zotero (frequência: a cada N horas)

| Arquivo | Última rotação | Conteúdo |
|---------|---------------|----------|
| `~/Zotero/zotero.sqlite.bak` | (rotaciona) | Snapshot mais recente automatizado |
| `~/Zotero/zotero.sqlite.1.bak` | (rotaciona) | Snapshot anterior (offset -1) |
| `~/Zotero/beaver.sqlite.bak` + `.1.bak` | (rotaciona) | Backup do plugin Beaver |

⚠️ **Atenção**: o `.bak` do Zotero é **sobrescrito periodicamente**. Não dependa dele pra "estado X horas atrás" — copie pra `diagnostics/` se quiser garantir.

### Snapshots de fases (em `diagnostics/`)

A serem criados antes de cada fase destrutiva. Nomenclatura:
- `zotero_snap_YYYY-MM-DD[_HHMM].sqlite` — snapshot pontual
- `zotero_BEFORE_<EVENTO>_YYYY-MM-DD.sqlite` — checkpoint rotulado pra evento específico

## Como fazer snapshot

### Opção A — Cópia simples do `.bak` (Zotero pode estar aberto)

```powershell
$ts = Get-Date -Format "yyyy-MM-dd_HHmm"
Copy-Item "$env:USERPROFILE\Zotero\zotero.sqlite.bak" `
          "C:\Users\Mancano\Documents\MancanoSync\mancano-zotero-library\diagnostics\zotero_snap_$ts.sqlite"
```

Vantagem: instantâneo, não precisa fechar Zotero
Desvantagem: estado do `.bak` pode estar N horas atrás (Zotero não rotaciona em tempo real)

### Opção B — Backup consistente do live (com Zotero aberto)

Usar a SQLite Online Backup API via Python (preserva estado do momento):

```python
import sqlite3
src = sqlite3.connect("file:C:/Users/Mancano/Zotero/zotero.sqlite?mode=ro", uri=True)
dst = sqlite3.connect("C:/Users/Mancano/Documents/MancanoSync/mancano-zotero-library/diagnostics/zotero_snap_now.sqlite")
src.backup(dst)
dst.close(); src.close()
```

Vantagem: estado do momento exato
Desvantagem: precisa Python; pode falhar se SQLite tiver lock exclusivo (raro)

### Opção C — Fechar Zotero + copiar `zotero.sqlite`

Mais seguro porém invasivo. Usar só pra grandes mudanças irreversíveis.

## Como restaurar

⚠️ **Sempre fechar o Zotero antes de restaurar.**

1. Fechar Zotero completamente (verificar tray + Task Manager)
2. Renomear arquivo atual pra histórico:
   ```powershell
   Move-Item "$env:USERPROFILE\Zotero\zotero.sqlite" `
             "$env:USERPROFILE\Zotero\zotero.sqlite.broken_$(Get-Date -Format yyyyMMdd_HHmm)"
   ```
3. Copiar snapshot pro lugar:
   ```powershell
   Copy-Item "C:\Users\Mancano\Documents\MancanoSync\mancano-zotero-library\diagnostics\zotero_BEFORE_REORG_2026-05-09.sqlite" `
             "$env:USERPROFILE\Zotero\zotero.sqlite"
   ```
4. Apagar journal se existir:
   ```powershell
   Remove-Item "$env:USERPROFILE\Zotero\zotero.sqlite-journal" -ErrorAction SilentlyContinue
   ```
5. Abrir Zotero — deve voltar pro estado do snapshot

### Custo de restaurar

**Perde-se tudo que foi adicionado após o snapshot**: papers novos, anotações, mudanças de coleção, tags aplicadas, etc. Por isso restaurar é sempre **opção de emergência**.

Se a alteração problemática for específica (ex: uma coleção mal-mesclada), considerar:
- Verificar **Lixeira do Zotero** primeiro (retenção 30 dias)
- Usar a Web API do Zotero pra recuperar itens individuais
- Restaurar do snapshot mais antigo possível pra minimizar perda

## Sync com nuvem Zotero

⚠️ **Verificar se sync está ligado** antes de fases grandes:
- Settings → Sync → Data Syncing
- Se ligado: pausar antes de scripts destrutivos pra evitar conflito com outros devices
- Reativar depois e deixar sincronizar
