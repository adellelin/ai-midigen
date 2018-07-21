FROM python:3.6
COPY ./ /midigen_install/

RUN cd midigen_install\
    && python setup.py bdist_wheel\
    && pip --no-cache-dir install "dist/$(ls dist)"\
    && cd ~\
    && rm -rf /midigen_install

COPY user_entrypoint.sh /usr/local/bin/entrypoint.sh
ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]
