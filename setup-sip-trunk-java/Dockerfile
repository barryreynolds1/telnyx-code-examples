FROM eclipse-temurin:21-jdk AS builder

WORKDIR /app

COPY pom.xml .
RUN mvn dependency:go-offline -B || true

COPY . .
RUN mvn package -DskipTests -B

FROM eclipse-temurin:21-jre

WORKDIR /app
COPY --from=builder /app/target/*.jar app.jar

RUN useradd -r appuser
USER appuser

EXPOSE 8080

CMD ["java", "-jar", "app.jar"]
