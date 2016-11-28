FROM eliostvs/tomate

WORKDIR /code

ENTRYPOINT ["make"]

CMD ["test"]
