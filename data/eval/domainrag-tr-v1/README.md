# KTMÜ DomainRAG Türkçe geliştirme taslağı

DomainRAG'ın yöntem ve alan düzeni KTMÜ'nün Türkçe kaynaklarına uyarlandı.
Çince kaynak, cevap veya uygulama kodu bu pakete aktarılmadı.

- `cases.jsonl`: 106 senaryo; `question`, `golden_answers`, `metadata` alanları.
- `corpus.jsonl`: iki yönetmelik ve üç SSS kaynağından 21 sayfa/bölüm.
- `manifest.json`: kaynak ve paket hash'leri, yöntem atfı ve görev sayıları.

**Taslak geliştirme verisidir; uzman onaylı gold veya LoRA eğitim verisi değildir.**
`golden_answers` alan adı biçim uyumluluğu içindir; içerik taslak referans cevaptır.
Kaynak sürümleri arşiv görüntüsüdür; güncel yürürlük doğrulanmamıştır.

100 kayıt mevcut 50 sorunun soru/varyantlarıdır. Altı ek senaryo; konuşma,
yapılandırılmış bilgi, kaynağa sadakat, yanıltıcı bağlam, güncellik ve birden çok
belge yeteneklerini örnekler. Her ek türün yalnız bir örneği olduğundan bu pilot
kapsamlı benchmark sayılmaz. Tüm kayıtlar aynı kural aileleri ve temel vaka
kimlikleriyle izlenir; train/test olarak yeniden etiketlenmez.

Konuşma geçmişi DomainRAG gibi `question` / `answers` çiftleri taşır; bunlar
üretim API'sinin kullanıcı/asistan mesajlarına çevrilir. Sentetik yanlış asistan
cevabı bir negatif test girdisidir ve kurumsal bilgi kaynağı değildir.
`metadata.query` bağımsız soru hedefidir; ölçüm aracı bunun yerine gerçek soruyu
ve üretimdeki bağlam çözücüsünü kullanır. `positive_reference` kaynak alıntılarını,
`context_ids` kontrollü üretimde gösterilecek kaynakları belirtir.

Üretim bilgi deposuna bu sorular/cevaplar indekslenmez. LoRA dışa aktarma yetkisi
oluşturulmaz; `scripts.dataset export` aracının insan incelemesi koşulları sürer.
Train veya saklı test kaynakları geliştirme paketine alınamaz.

Komutlar, inceleme ve sonuçlar:
[Entegrasyon raporu](../../../docs/evaluation/domainrag-tr-v1/README.md).
