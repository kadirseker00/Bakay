// Kaynak: KTMÜ Vize Birimi, "Çalışanlar ve Aile Bireyleri İçin Vize Yönergesi"
// (son düzenleme 21.09.2026). Aynı metin indekste
// docs/rehber/tr_staff_vize_yonergesi_2026-09-21.md (canlıda data/raw/staff/) olarak bulunur;
// yönerge değişirse ikisi birlikte güncellenmelidir.

export const SOURCE = {
  title: "Çalışanlar ve Aile Bireyleri İçin Vize Yönergesi",
  unit: "KTMÜ Vize Birimi",
  updated: "21.09.2026",
  regulation: "09.05.2026",
};

export type MapLink = { label: string; yandex?: string; google?: string };

export type Step = {
  id: string;
  no: string;
  title: string;
  local?: string;
  summary: string;
  where?: MapLink[];
  cost?: string;
  points: string[];
  warning?: string;
};

export const STEPS: Step[] = [
  {
    id: "ceviri",
    no: "1",
    title: "Noter onaylı çeviriler",
    local: "Kırgızca tercüme + noter onayı",
    summary: "Her şey çeviriyle başlar: PIN için pasaport, eşin vizesi için evlilik cüzdanı.",
    points: [
      "Pasaport: noter onaylı Kırgızca tercüme (PIN başvurusu için).",
      "Eş: evlilik (aile) cüzdanının noter onaylı Kırgızca tercümesi; vize başvurusunda aslıyla birlikte istenir.",
      "Çocuk: nüfus cüzdanının noter onaylı Kırgızca tercümesi.",
      "Cal’da Şeroy’un içinde noter ve tercüme işleri yapan yer var. Daha önce verilen çeviriler yeniden istenmez.",
    ],
  },
  {
    id: "pin",
    no: "2",
    title: "PIN numarası",
    local: "ЦОН · Nüfus Dairesi",
    summary: "Sigorta, sağlık raporu ve AIDS testi için PIN şart. Daha önce aldıysanız aynısını kullanın.",
    where: [{
      label: "Nikâh Dairesi 2. kat · 121 Jumabeka St, Bişkek",
      yandex: "https://yandex.com/maps/-/CTs9vJ~q",
      google: "https://maps.app.goo.gl/rYxWMVg4mppf9zNNA",
    }],
    points: [
      "PIN, pasaportun noter onaylı Kırgızca tercümesiyle Nüfus Dairesine kişisel başvuruyla alınır.",
      "Çocuklar için PIN, okula gidecekse gereklidir.",
      "Başka nüfus müdürlükleri işlemi yapmayıp sizi bu adrese yönlendirebilir.",
    ],
  },
  {
    id: "sigorta",
    no: "3",
    title: "Zorunlu sağlık sigortası",
    local: "Милдеттүү Медициналык Камсыздандыруу (ММК)",
    summary: "İlk iş sigorta: sağlık heyet raporu sigortasız yapılmaz.",
    cost: "1840 som · yalnız Eldik Bank",
    where: [{
      label: "Eldik Bank (Cal) · Jal-23 mikrorayon, 101",
      yandex: "https://yandex.com/maps/-/CXcpjHzh",
    }],
    points: [
      "Pasaportunuzla Eldik Bank’a gidip aşağıdaki hesap bilgileriyle ödeyin. Sizin yerinize başkası ödeyecekse pasaport kopyanızı verin.",
      "Dekont ve pasaportla Vize Biriminde sigorta işlerine bakan Kıyal Hanım’a gidin; işlem 3 gün içinde sonuçlanır.",
      "Aile bireylerinin sigortası farklı yapılır; Kıyal Hanım’la görüşün.",
      "Poliçenin çıktısını almayın; telefona indirin, başvuruda WhatsApp’tan gönderilecek.",
    ],
    warning: "Başka banka veya ödeme yoluyla yapılırsa ücret 12000 som olur.",
  },
  {
    id: "rapor",
    no: "4",
    title: "Sağlık heyet raporu (086)",
    local: "086/У формасындагы медициналык маалымкат · “nöl 86 spravkası”",
    summary: "Devlet polikliniğinden alınır; Manas dil hazırlık binasının hemen yakınında.",
    where: [{
      label: "2 No’lu Poliklinik · Ishembay Abdraimov St 25/1, oda 304",
      yandex: "https://yandex.com/maps/-/CTwxbOzo",
      google: "https://maps.app.goo.gl/Hp2JGKBWHggZn1bf7",
    }],
    points: [
      "304 numaralı odada Anarkan Ece’ye (Tölöşeva) Manas Üniversitesinden geldiğinizi ve 086 raporu alacağınızı söyleyin.",
      "Rapor elle doldurulmuş verilirse önlü arkalı fotoğrafı yeterli; raporun kendisini getirmeyin.",
    ],
    warning: "Özel hastaneden veya Kırgızistan dışından alınan rapor kabul edilmez.",
  },
  {
    id: "aids",
    no: "5",
    title: "AIDS / HIV testi",
    local: "“Spid cönündö spravka”",
    summary: "Sağlık raporundan bağımsız, ayrı bir belge. Kan alımı hafta içi 12.00’ye kadar.",
    where: [
      {
        label: "Logvinenko 8 · sonuç ertesi gün online",
        yandex: "https://yandex.com.tr/maps/-/CTskJ-k7",
        google: "https://maps.app.goo.gl/9TAzDnU2cHeXm4HM7",
      },
      {
        label: "Toktogul 62 · hızlı, sonuç elden alınır",
        yandex: "https://yandex.com.tr/maps/-/CTskNF9B",
        google: "https://maps.app.goo.gl/wemqNexKLroQwvUZA",
      },
    ],
    points: [
      "Online sonuç: ilab.med.kg sonuç sayfasında pasaport numaranızı (U12345678 biçiminde) ve pasaporta yapıştırılan numarayı girin, ПОИСК’e basın.",
      "Sonucun ekran görüntüsü veya PDF’i kabul edilir.",
    ],
    warning: "Özel hastaneden veya Kırgızistan dışından alınan test sonucu kabul edilmez.",
  },
  {
    id: "basvuru",
    no: "6",
    title: "Vize uzatma başvurusu",
    local: "Vize Birimi",
    summary: "Vize bitiminden 1 ay önce, eksiksiz belgeyle başvurun.",
    points: [
      "Sigorta, rapor ve test görüntüleri telefonda hazır olsun; başvuruda WhatsApp’tan gönderilir.",
      "Sigorta ve rapor görüntülerini PDF yapmayın (AIDS sonucu PDF olabilir); çıktı ya da asıl belge getirmeyin.",
      "Vize ücreti QR ile ödenir; nakit alınmaz.",
    ],
    warning: "Eksik evrakla gelen başvuru kabul edilmez.",
  },
];

export const PAYMENT = [
  { label: "Лицевой счет (hesap)", value: "4402013001001916" },
  { label: "Банк получателя", value: "ЦКМФКР" },
  { label: "БИК", value: "440201" },
  { label: "Код платежа", value: "12311200" },
  { label: "ИИН", value: "00402199710059" },
  { label: "Назначение платежа", value: "Лица, самостоятельно уплачивающие за страховой полис ОМС г.Бишкек" },
  { label: "Tutar", value: "1840 som" },
];

export const AIDS_RESULT_URL = "https://ilab.med.kg/Result/AnalysisResultByPinBarcodeForCitizens";

export const CHECKLISTS = [
  {
    id: "calisan",
    title: "Çalışanlar",
    items: [
      { text: "Vesikalık fotoğraf", note: "Daha önce verildiyse gerekmez" },
      { text: "Pasaportun aslı" },
      { text: "Zorunlu sağlık sigortası poliçesi", note: "Ekran görüntüsü" },
      { text: "Sağlık heyet raporu (086)", note: "Önlü arkalı fotoğraf" },
      { text: "AIDS test sonucu", note: "Ekran görüntüsü veya PDF" },
      { text: "Vize ücreti", note: "QR ile, nakit değil" },
    ],
  },
  {
    id: "aile",
    title: "Aile bireyleri",
    items: [
      { text: "Vesikalık fotoğraf", note: "Daha önce verildiyse gerekmez" },
      { text: "Pasaportun aslı" },
      { text: "Zorunlu sağlık sigortası poliçesi", note: "Ekran görüntüsü · işlem farklı, Kıyal Hanım’a danışın" },
      { text: "086 sağlık raporu", note: "Önlü arkalı fotoğraf" },
      { text: "AIDS test sonucu", note: "Ekran görüntüsü veya PDF" },
      { text: "Eş: aile cüzdanı aslı + noter onaylı Kırgızca tercümesi", note: "Daha önce verildiyse gerekmez" },
      { text: "Çocuk: nüfus cüzdanı aslı + noter onaylı Kırgızca tercümesi", note: "Daha önce verildiyse gerekmez" },
      { text: "Vize ücreti", note: "QR ile, nakit değil" },
    ],
  },
];

export const RULES = [
  { title: "2,5 ay geçerlilik", text: "Sigorta, rapor ve test, alındıkları tarihten itibaren 2,5 ay geçerli. Türkiye’den alınan belgeler kabul edilmez." },
  { title: "Sıra önemli", text: "Önce sigorta, sonra diğer belgeler. Aksi hâlde ücret farkı çıkabilir." },
  { title: "Yalnız çok girişli vize", text: "Tek girişli vize kaldırıldı." },
  { title: "Vizesiz aile bireyi", text: "Önce 3 aylık çok girişli vize, sonra 4–12 aylık uzatma. Giriş vizesi için sigorta/rapor/test gerekmez." },
  { title: "18 yaş ve üstü", text: "18 yaşını doldurmuş aile bireylerine Üniversite üzerinden vize alınamaz." },
  { title: "15 yaş altı", text: "Sağlık raporu, AIDS testi ve sigorta istenmez." },
  { title: "Burada pasaport yenilerseniz", text: "Vizenin yeni pasaporta transferi gerekir (ortalama 5 iş günü); eski ve yeni pasaport, vize ve oturumla Vize Birimine başvurun. Transferden sonra oturumu ЦОН’da yeniden yaptırmanız gerekir." },
  { title: "Türkiye’de pasaport yenilerseniz", text: "Eski pasaportu iptal ettirmeyin ve Kırgızistan’a onunla girin; yoksa sınırda içeri alınmazsınız." },
];

export const QUESTIONS = [
  "Eşimin vizesini uzatmak için hangi belgeler gerekiyor?",
  "Sigorta ödemesini Eldik Bank dışında yaparsam ne olur?",
  "086 sağlık raporunu nereden alabilirim?",
  "Türkiye'de pasaportumu yenilersem vizem ne olur?",
  "15 yaşından küçük çocuğum için sağlık raporu gerekir mi?",
];
