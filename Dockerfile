FROM ubuntu:14.04

RUN apt-get install -y -qq wget

RUN wget -O- http://download.opensuse.org/repositories/home:/eliostvs:/tomate/xUbuntu_14.04/Release.key | apt-key add -
RUN echo 'deb http://download.opensuse.org/repositories/home:/eliostvs:/tomate/xUbuntu_14.04/ ./' > /etc/apt/sources.list.d/tomate.list

COPY ./ /code/

RUN apt-get update -qq && apt-get install -y \
	gir1.2-glib-2.0 \
	make \
	python-blinker \
	python-coverage \
	python-dbus \
	python-enum34 \
	python-gi \
	python-mock \
	python-nose \
	python-six \
	python-wiring \
	python-wrapt \
	python-xdg \
	python-yapsy

RUN apt-get clean

WORKDIR /code/

ENTRYPOINT ["make"]

CMD ["test"]