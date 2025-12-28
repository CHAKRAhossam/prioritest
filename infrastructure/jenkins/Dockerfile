FROM jenkins/jenkins:lts

USER root

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    wget \
    git \
    unzip \
    && rm -rf /var/lib/apt/lists/*

# Install Maven
RUN curl -fsSL https://archive.apache.org/dist/maven/maven-3/3.9.6/binaries/apache-maven-3.9.6-bin.tar.gz | tar xzf - -C /opt && \
    ln -s /opt/apache-maven-3.9.6 /opt/maven && \
    chmod -R 755 /opt/maven

# Install Python 3 and pip with build dependencies
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    build-essential \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Node.js 20.x LTS
RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash - && \
    apt-get install -y nodejs && \
    rm -rf /var/lib/apt/lists/*

# Install jq for JSON parsing
RUN apt-get update && apt-get install -y jq && \
    rm -rf /var/lib/apt/lists/*

# Install Rust (required for pydantic-core compilation)
RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
RUN . $HOME/.cargo/env && \
    rustc --version && \
    cargo --version
RUN echo 'source $HOME/.cargo/env' >> /root/.bashrc && \
    echo 'export CARGO_HOME=$HOME/.cargo' >> /root/.bashrc && \
    echo 'export RUSTUP_HOME=$HOME/.rustup' >> /root/.bashrc && \
    echo 'export PATH=$CARGO_HOME/bin:$PATH' >> /root/.bashrc

# Install SonarQube Scanner
RUN wget https://binaries.sonarsource.com/Distribution/sonar-scanner-cli/sonar-scanner-cli-5.0.1.3006-linux.zip -O /tmp/sonar-scanner.zip && \
    unzip /tmp/sonar-scanner.zip -d /opt && \
    mv /opt/sonar-scanner-* /opt/sonar-scanner && \
    rm /tmp/sonar-scanner.zip && \
    chmod -R 755 /opt/sonar-scanner

# Set environment variables (available for all users)
ENV MAVEN_HOME=/opt/maven
ENV SONAR_SCANNER_HOME=/opt/sonar-scanner
ENV CARGO_HOME=/root/.cargo
ENV RUSTUP_HOME=/root/.rustup
ENV PATH="${CARGO_HOME}/bin:${MAVEN_HOME}/bin:${SONAR_SCANNER_HOME}/bin:${PATH}"

# Keep root user (Jenkins runs as root in docker-compose.yml)
# This allows access to Docker socket and all tools

# Verify installations (find and use Java from Jenkins base image)
RUN JAVA_HOME=$(dirname $(dirname $(readlink -f $(which java)))) && \
    export JAVA_HOME && \
    export CARGO_HOME=/root/.cargo && \
    export RUSTUP_HOME=/root/.rustup && \
    export PATH=$CARGO_HOME/bin:$PATH && \
    if [ -f /root/.cargo/env ]; then . /root/.cargo/env; fi && \
    mvn --version && \
    python3 --version && \
    pip3 --version && \
    node --version && \
    npm --version && \
    jq --version && \
    rustc --version && \
    cargo --version && \
    sonar-scanner --version && \
    echo "All tools installed successfully!" && \
    echo "JAVA_HOME=${JAVA_HOME}"

