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

# Install Python 3 and pip
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    && rm -rf /var/lib/apt/lists/*

# Install Node.js 20.x LTS
RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash - && \
    apt-get install -y nodejs && \
    rm -rf /var/lib/apt/lists/*

# Install jq for JSON parsing
RUN apt-get update && apt-get install -y jq && \
    rm -rf /var/lib/apt/lists/*

# Set environment variables (available for all users)
ENV MAVEN_HOME=/opt/maven
ENV PATH="${MAVEN_HOME}/bin:${PATH}"
ENV JAVA_HOME=/usr/local/openjdk-17

# Keep root user (Jenkins runs as root in docker-compose.yml)
# This allows access to Docker socket and all tools

# Verify installations
RUN mvn --version && \
    python3 --version && \
    pip3 --version && \
    node --version && \
    npm --version && \
    jq --version && \
    echo "All tools installed successfully!"

