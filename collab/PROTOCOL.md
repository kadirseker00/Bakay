# Ajan İşbirliği Protokolü (Claude ↔ Codex)

Bu repoda iki kodlama ajanı eş zamanlı çalışır: **Claude** (Claude Code) ve
**Codex** (OpenAI Codex CLI). Çakışmayı önlemek ve haberleşmek için bu protokol
uygulanır. Dosyalar git ile takip edilir; iletişim bu dosyalar üzerinden yürür.

## Dosyalar

| Dosya | Amaç | Kim yazar |
|---|---|---|
| `collab/board.md` | Görev panosu: kim neyi yapıyor, hangi dosyalar kilitli | İkisi de (yalnız kendi satırları) |
| `collab/to-codex.md` | Claude → Codex mesajları | Claude ekler, Codex işaretler |
| `collab/to-claude.md` | Codex → Claude mesajları | Codex ekler, Claude işaretler |

## Kurallar

1. **Oturum başında** önce `collab/board.md` ve kendi gelen kutunu
   (`to-claude.md` / `to-codex.md`) oku. Okuduğun mesajın kutusunu `[x]` yap.
2. **İş almadan önce** panoya satır ekle: görev, sahibi, tarih ve dokunacağın
   dosya/dizinler. Diğer ajanın panoda sahiplendiği dosyalara **dokunma**.
3. **Mesaj bırakmak için** karşı tarafın gelen kutusuna en alta ekle:
   `- [ ] YYYY-MM-DD HH:MM <gönderen>: <mesaj>`. Var olan mesajları silme,
   düzenleme; sadece kendi mesajını ekle, okuduğunu `[x]` yap.
4. **İş bitince** panodaki satırını `✅` yap, kilidi düşür ve gerekiyorsa karşı
   tarafa özet mesaj bırak (ne değişti, hangi dosyalar, dikkat edilecekler).
5. **Commit'ler küçük ve sık** olsun; commit mesajında ajan adı geçsin
   (`[claude] ...` / `[codex] ...`). Aynı dosyada çakışma çıkarsa panoda
   kilitli olan kazanır, diğeri rebase eder.
6. **Kararsızlıkta** kullanıcıya sor; ajanlar birbirinin kararını iptal etmez,
   itirazını mesaj kutusuna yazar.

## Görev bölüşümü

Varsayılan bölüşüm panoda tutulur; kullanıcı değiştirebilir.
