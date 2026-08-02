# Yol Haritası

[English](TODO.md) | **Türkçe**

## Dokümantasyon

- [x] İngilizce ve Türkçe seçeneklerini birlikte göster ve etkin belge dilini belirt.

## Kalite Güvencesi

- [x] Cross-platform ortam testlerinde çözümlenen geçici yolları normalize et.
- [x] Küçük harfli Conventional Commit başlıklarında 45 karakter sınırını uygula.

## Ayar Dosyasını Bulma

- [ ] En yakın `.venvm.json` dosyasını bulmak için üst dizinleri tara.
- [ ] Dosya sistemi kökünde veya açıkça belirtilen proje sınırında taramayı durdur.
- [ ] Tanılama çıktısında algılanan proje kökünü göster.

## Ayar Katmanları

- [ ] Ayarları yüksekten düşüğe şu öncelikle uygula: komut satırı seçenekleri,
  `VENVM_*` ortam değişkenleri, `.venvm.local.json`, `.venvm.json`, global
  kullanıcı ayarları ve yerleşik varsayılanlar.
- [ ] Global ayarları platforma uygun kullanıcı dizininde sakla:
  - Windows: `%APPDATA%\venvm\config.json`
  - Linux: `${XDG_CONFIG_HOME:-~/.config}/venvm/config.json`
  - macOS: `~/Library/Application Support/venvm/config.json`
- [ ] Gelecekteki geçişler için ayar şeması sürümü ekle.
- [ ] Yarım dosya oluşmasını önlemek için ayar değişikliklerini atomik olarak yaz.

## Ayar Komutları

- [ ] Etkin ayar yollarını yazdıran `venvm config path` komutunu ekle.
- [ ] Saklanan değerleri gösteren `venvm config show` komutunu ekle.
- [ ] Birleştirilmiş değerleri ve kaynaklarını gösteren
  `venvm config show --effective` komutunu ekle.
- [ ] `venvm config get KEY` komutunu ekle.
- [ ] Proje, yerel ve global kapsamları destekleyen
  `venvm config set KEY VALUE` komutunu ekle.
- [ ] `venvm config unset KEY` komutunu ekle.
- [ ] Geçersiz yolları ve ayar çakışmalarını bildiren
  `venvm config doctor` komutunu ekle.

## Yerel Ayarlar

- [ ] Geliştiriciye özel ayarlar için `.venvm.local.json` desteği ekle.
- [ ] venvm tarafından oluşturulduğunda `.venvm.local.json` dosyasını
  `.gitignore` içine ekle.
- [ ] Paylaşılan varsayılanları `.venvm.json`, makineye özel yolları yerel dosyada tut.

## Proje Başlatma

- [ ] İnteraktif `venvm init` komutunu ekle.
- [ ] `venvm init` ile varsayılan ortam, script veya modül seçilebilmesini sağla.
- [ ] `venvm init` komutunun onay alarak `.venvm.json` oluşturmasını ve
  `.gitignore` dosyasını güncellemesini sağla.

## Merkezi Proje Kaydı

- [ ] Proje adını yoluyla eşleştiren `venvm register NAME` komutunu ekle.
- [ ] Kayıtlı projeleri listeleyen `venvm projects` komutunu ekle.
- [ ] Kayıtlı proje için venvm çalıştıran `venvm use NAME` komutunu ekle.
- [ ] `venvm unregister NAME` komutunu ekle.
- [ ] Yalnızca proje adlarını ve yollarını sakla; sanal ortamları taşıma.
- [ ] Artık bulunmayan proje yollarını algıla ve bildir.

## Ortam Değişkenleri

- [ ] Tercih edilen ortam için `VENVM_ENV` desteği ekle.
- [ ] Açıkça belirtilen ayar dosyası için `VENVM_CONFIG` desteği ekle.
- [ ] İnteraktif olmayan çalıştırma için `VENVM_NO_INPUT` desteği ekle.

## Güvenlik

- [x] Bağımlılık dosyalarını interaktif olmadan kurmadan önce
  `--install-deps` seçeneğini zorunlu tut.
- [x] `--yes` seçeneğinin tek başına klonlanan bir depodan bağımlılık kurmasına izin verme.
- [ ] Proje veya global venvm ayarlarında gizli bilgi saklama.
- [ ] Çalıştırmadan önce ayarlanan ortam ve proje yollarını doğrula.
