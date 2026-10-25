CNCjs Bridge Companion v0.3.0 — testowa integracja HACS
Nowe natywne encje: `select` (wybór pliku), `button` (odśwież, załaduj, start, pauza, wznów, stop). Nie wymaga ręcznego tworzenia pomocników ani skryptów. Zachowuje istniejące czujniki, token/login, katalog G-code i ikony.
Instalacja
Prześlij katalog `custom_components/cncjs_bridge_companion` do repozytorium GitHub, zaktualizuj przez HACS, zrestartuj Home Assistant. Nie trzeba zmieniać `bridge.js`.
W ustawieniach integracji podaj katalog `/media/laser`. Jeśli bridge nie publikuje atrybutu `port` lub `serial_port`, w opcjach podaj port kontrolera, zwykle `/dev/ttyUSB0`. Port jest wykorzystywany przez CNCjs; integracja nie otwiera go bezpośrednio.
Panel
W edytorze dashboardu dodaj kartę Encje i wybierz nowo utworzone encje `Plik G-code`, `Odśwież pliki`, `Załaduj plik`, `Pauza`, `Stop`. Nazwy entity_id ustala Home Assistant.
Ograniczenia bezpieczeństwa
Nie używaj przycisków do sterowania aktywnym laserem, dopóki nie zweryfikujesz protokołu z CNCjs 1.11.5. Start i Wznów są celowo zablokowane w natywnych przyciskach, aby nie dopuścić do przypadkowego uruchomienia. Akcja legacy `cncjs_bridge_companion.control` pozostaje dostępna i eksperymentalna. `Załaduj plik` wysyła żądanie Socket.IO, ale brak potwierdzenia odbioru z CNCjs. Testuj bez zasilania modułu laserowego i bez materiału.
Postęp zadania jest zależny od danych bridge i nie jest jeszcze osobnym czujnikiem. Lista obejmuje pliki z lokalnego katalogu HA, nie bibliotekę plików CNCjs.


-----------------------------------------------------------------------



# CNCjs Bridge Companion v0.2.3

Osobna integracja Home Assistant, współpracująca z istniejącym `bridge.js`.
Nie zastępuje usługi Node.js ani sterowania LED WS2812.

## Wymagania
- Działający bridge, który zapisuje stan do `sensor.cncjs_status` przez REST API Home Assistant.
- Home Assistant z obsługą integracji niestandardowych.

## Instalacja ręczna
Skopiuj `custom_components/cncjs_bridge_companion` do katalogu `config/custom_components/` Home Assistant, uruchom ponownie HA i dodaj integrację `CNCjs Bridge Companion` w Ustawienia → Urządzenia i usługi → Dodaj integrację. Wybierz `sensor.cncjs_status`.

## Instalacja przez HACS
Dodaj adres repozytorium jako niestandardowe, wybierz typ repozytorium  Integracja, uruchom ponownie HA.

## Encje
- Status — kopia stanu istniejącego `sensor.cncjs_status` z atrybutami.
- Połączenie CNCjs — z atrybutu `socket_connected`.
- Połączenie USB lasera — z atrybutu `serial_connected`.
- Zadanie aktywne — z atrybutu `job_active`.

Integracja działa lokalnie i reaguje na zmiany encji źródłowej; nie łączy się bezpośrednio z CNCjs. Oryginalna encja i automatyzacje pozostają bez zmian. Jeśli bridge przestanie aktualizować encję, ostatni stan może pozostać widoczny — ta wersja nie wykrywa utraty połączenia z cncjs-bridge-ha  na podstawie czasu.

**Bezpieczeństwo:** status programu nie jest niezależnym potwierdzeniem zatrzymania lasera. Nie używaj tych encji jako jedynego zabezpieczenia.

## Repozytoria
- Integracja HACS: https://github.com/dru0/cncjs-bridge-ha-integration
- Bridge Raspberry Pi: https://github.com/dru0/cncjs-bridge-ha



