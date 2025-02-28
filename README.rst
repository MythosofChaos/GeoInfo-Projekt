.. _User_Documentation:
==================
User Documentation
==================

Das Projekt zielt darauf ab, die Verbreitung von Wüstenpflastern mithilfe von Social-Media-Daten von Flickr und KI-gestützter Bildklassifikation mittels GroundingDINO zu erfassen.

==================
Inhaltsverzeichnis
==================
1. Technische Anforderungen
2. Installationsanleitung
3. Ordnerstruktur
4. Skript-Dokumentation
   - extract_coordinates.py
   - photo_download.py
   - color_detection_multiple.py
   - desertpavement_prediction_multiple.py
5. Togglebare Variablen
6. Lizenzinformationen

==================
Technische Anforderungen
==================
- Python 3.12.x (empfohlen 3.12.8)
- CUDA 11.x (empfohlen 11.7)
- PyTorch 2.5.x (empfohlen 2.5.1)
- NVIDIA GPU mit 3GB VRAM (für GroundingDINO)
- 10 GB freier Festplattenspeicher
- Flickr API-Schlüssel (kostenloses Konto erforderlich)

==================
Installation
==================
1. Grundinstallation: 
   
   - Eine genauere Anleitung zur Installation von GroundingDINO finden Sie im `offiziellen Repository`_
   - Es wird empfohlen, GroundingDINO in das Root-Verzeichnis des Projekts zu klonen.
   
.. code-block:: bash
        
        git clone https://github.com/IDEA-Research/GroundingDINO.git
        cd GroundingDINO
        pip install -r requirements.txt
        python setup.py install
   
   
2. Projektabhängigkeiten installieren:

   pip install geopandas folium scikit-learn opencv-python flickrapi python-dotenv

3. Umgebungsvariablen einrichten:
   
   Erstellen Sie `.env`-Datei mit Flickr-API-Schlüsseln:

.. code-block:: bash
        
        FLICKR_API_KEY="Ihr-Schlüssel"
        FLICKR_SECRET_KEY="Ihr-Geheimschlüssel"
     

.. _offiziellen Repository: https://github.com/IDEA-Research/GroundingDINO
==================
Ordnerstruktur
==================
Projekt-Root/

├── in/

│   ├── 1976-2000.shp          # Klimaklassifikations-Shapefile

│   └── FlickrAPI_keys.env     # API-Schlüssel

├── out/

│   ├── downloaded_photos/     # Rohbilder von Flickr

│   ├── possible_desert_pavements/  # RGB-gefilterte Bilder

│   └── annotated_*/           # KI-klassifizierte Ergebnisse

├── output/                    # Generierte Bounding-Boxes

└── GroundingDINO/             # Clone des offiziellen Repositories

==================
Skript-Dokumentation
==================

extract_coordinates.py
----------------------
**Funktion**: Extrahiert Bounding-Boxes aus Klimazonen-Shapefiles

1. Input:
   - Shapefile: in/1976-2000.shp
   - Klimazonen-Codes (GRIDCODE 21=BWh, 22=BWk)

2. Output:
   - CSV: output/bounding_boxes.csv
   - Interaktive Karte: output/bounding_boxes_map.html

3. Ausführung:
   :code:`python scripts/extract_coordinates.py`


photo_download.py
-----------------
**Funktion**: Lädt Bilder von Flickr herunter

1. Konfiguration:
   - Suchbegriff: "desert pavement"
   - Max. Downloads: 68,000 (anpassbar über DOWNLOAD_LIMIT)
   - Die Flickr API ist limitiert auf 3600 Anfragen pro Stunde

2. Output:
   - Bilder: out/downloaded_photos/*.jpg
   - Metadaten: out/data.json

3. Ausführung:
   :code:`python scripts/photo_download.py`


color_detection_multiple.py
---------------------------
**Funktion**: RGB-basierte Vorauswahl

1. Input:
   - Bilder: out/downloaded_photos/

2. Output:
   - Positivfälle: out/possible_desert_pavements/
   - Negativfälle: out/no_desert_pavement/

3. Parameter:
   - Farbtoleranz: 50% (Zeile 96: desert_percentage > 50)

4. Ausführung:
   :code:`python scripts/color_detection_multiple.py`


desertpavement_prediction_multiple.py
-------------------------------------
**Funktion**: KI-gestützte Objekterkennung

1. Input:
   - Bilder: out/possible_desert_pavements/

2. Output:
   - Annotierte Bilder: out/annotated_desert_pavements/
   - Log-Daten: groundingdino_scripts/logits_phrases_all.json

3. Wichtige Parameter (Zeilen 30-35):
   TEXT_PROMPT = "road markings . desert pavement ..."  # Suchbegriffe
   BOX_THRESHOLD = 0.35   # Minimale Box-Konfidenz
   TEXT_THRESHOLD = 0.25  # Minimale Text-Konfidenz

4. Ausführung:
   :code:`python scripts/desertpavement_prediction_multiple.py`


==================
Togglebare Variablen
==================

1. photo_download.py:

.. code-block:: bash
   PRINT_DEBUG_INFO = True  # Zeigt Download-Fortschritt
   PRINT_DEBUG_INFO_PHOTO_NAMES = True  # Listet Dateinamen

2. desertpavement_prediction_*.py:
   
.. code-block:: bash
   use_annotated_as_origin = True  # Zweiter Durchlauf mit annotierten Bildern
    
3. color_detection_*.py:
   
.. code-block:: bash
   desert_ranges = [...]  # RGB-Werte für Wüstenpflaster

4. desertpavement_prediction_multiple.py:
   
.. code-block:: bash
   draw_boxes = True  # Toggle für Bounding-Box Annotationen (Boxen, Text, Logits)
   
   Wir haben die Annotation-Funktion von GroundingDINO so modifiziert, dass die Anzeige von Bounding-Boxen und Labels optional ist. Diese Änderung wurde vorgenommen, um die Flexibilität der Bildanalyse zu erhöhen und die visuelle Darstellung der Ergebnisse an unsere spezifischen Anforderungen anzupassen. Die Anpassungen sind im Code durch den Parameter draw_boxes (Standardwert: True) in der Funktion annotate() gekennzeichnet.
   Dies ist insbesondere Hilfreich für multiple Durchläufe, damit die Bounding-Boxen nicht mitklassifizert werden.

In einigen Skripts finden sich zusätzlich :code:`DEBUG`-Flags zur Fehlerdiagnose.

==================
Lizenz
==================
Dieses Projekt verwendet GroundingDINO, ursprünglich entwickelt von IDEA Research, lizenziert unter der Apache-Lizenz, Version 2.0. Eigenentwickelte Skripte stehen unter MIT-Lizenz. Beachten Sie die Flickr-Nutzungsbedingungen für heruntergeladene Bilder.

Copyright 2024 - Projektteam Geoinformatik, FSU Jena
