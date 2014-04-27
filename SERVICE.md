Thumbnailer
============

1. Install libreoffice version 3.5
	sudo apt-get install libreoffice

2. Start a headless soffice:
	soffice --accept="socket,host=localhost,port=2002;urp;" --headless --invisible --nocrashreport --nodefault --nofirststartwizard --nologo --norestore &

3. Download the python thumbnailer library.
	git clone https://github.com/danisla/thumbnailer.git

4. Start the service
	cd thumbnailer
	python service.py