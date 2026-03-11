FROM python:3.11-slim

SHELL ["/bin/bash", "-o", "pipefail", "-c"]

ENV DEBIAN_FRONTEND=noninteractive
ENV HERMES_HOME=/home/aptale/.hermes
ENV PATH=/home/aptale/.local/bin:${PATH}

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        bash \
        ca-certificates \
        curl \
        git \
        gnupg \
        tini \
    && curl -fsSL https://deb.nodesource.com/setup_22.x | bash - \
    && apt-get install -y --no-install-recommends nodejs \
    && rm -rf /var/lib/apt/lists/*

# Hermes bridge features (Browserbase + WhatsApp/Baileys) require Node.js.
RUN node --version \
    && npm --version

# Install Hermes CLI from official installer script (same path used by local setup).
RUN curl -fsSL https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.sh | bash \
    && command -v hermes >/dev/null

RUN useradd --create-home --shell /bin/bash aptale
RUN mkdir -p /opt/aptale "${HERMES_HOME}" \
    && chown -R aptale:aptale /opt/aptale /home/aptale

WORKDIR /opt/aptale
COPY --chown=aptale:aptale . /opt/aptale

USER aptale

ENTRYPOINT ["/usr/bin/tini", "--"]
CMD ["bash", "-lc", "hermes gateway"]
