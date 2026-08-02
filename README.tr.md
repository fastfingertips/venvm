# venvm

[English](README.md) | **Türkçe**

`venvm`, bulunduğunuz dizindeki Python sanal ortamını seçip bir Python scriptini
veya modülünü o ortamın yorumlayıcısıyla çalıştıran komut satırı aracıdır.

## Kurulum

Geliştirme sürümünü depodan kurmak için:

```console
python -m pip install -e .
```

## Kullanım

Ortamı ve scripti interaktif olarak seçme:

```console
venvm
```

Bir scripti argümanlarıyla çalıştırma:

```console
venvm app.py --port 8000
```

Belirli bir ortamı veya sistem Python'unu kullanma:

```console
venvm --env .venv app.py
venvm --system app.py
```

Python modülü çalıştırma:

```console
venvm --env .venv --module pytest -q
venvm --system --module http.server 8000
```

`--module` sonrasındaki değerler doğrudan modüle aktarılır. Ortam seçenekleri
`--module` seçeneğinden önce yazılmalıdır.

Ortamları herhangi bir şey çalıştırmadan listeleme:

```console
venvm --list
```

`--yes` onay sorularını kabul eder. Birden fazla ortam varsa `.venv` kullanılır.
`.venv` yoksa ortam `--env` ile belirtilmelidir.

Algılanan bağımlılık kaynaklarını ek onay olmadan kurmak için `--install-deps`
kullanın. `--yes` tek başına bağımlılıkları otomatik olarak kurmaz.

Komut, mevcut dizinin doğrudan altındaki `pyvenv.cfg` dosyasına ve platforma
uygun Python yorumlayıcısına sahip ortamları tarar. Ortam yoksa `.venv`
oluşturmayı teklif eder. Sistem Python'u ayrıca seçilebilir.

Yeni bir ortam oluşturulduktan sonra `requirements.txt`,
`requirements-dev.txt` ve `pyproject.toml` algılanır. Her kaynak kurulmadan önce
onay istenir.

## Proje Ayarları

Varsayılanları tanımlamak için proje köküne `.venvm.json` ekleyin:

```json
{
  "environment": ".venv",
  "script": "app.py"
}
```

Modül çalıştırmak için:

```json
{
  "environment": ".venv",
  "module": "pytest"
}
```

`script` ve `module` aynı anda kullanılamaz. Komut satırında verilen değerler
ayar dosyasındaki varsayılanların önüne geçer.

## Geliştirme

Standart kütüphane testlerini çalıştırma:

```console
python -m unittest discover -s tests
```

## Yol Haritası

Planlanan ayar ve proje yönetimi çalışmaları
[`.github/TODO.tr.md`](.github/TODO.tr.md) dosyasında takip edilmektedir.
