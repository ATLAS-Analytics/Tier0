FROM atlasanalyticsservice/analytics-ingress-base:latest

LABEL maintainer Ilija Vukotic <ivukotic@cern.ch>

WORKDIR /home/analyticssvc

USER root

COPY *.py /home/analyticssvc/
COPY run.sh /

CMD [ "sleep","9999999" ]