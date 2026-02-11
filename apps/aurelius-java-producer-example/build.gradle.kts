import dev.nx.gradle.nx

nx {
    set("name", "aurelius-java-producer-example")
}

plugins {
    application
}

repositories {
    mavenCentral()
    maven {
        url = uri("https://packages.confluent.io/maven/")
    }
}

dependencies {
    testImplementation(libs.junit.jupiter)
    testImplementation(libs.mockito.core)
    testImplementation(libs.mockito.junit.jupiter)

    testRuntimeOnly("org.junit.platform:junit-platform-launcher")

    // Local dependencies
    implementation(project(":aurelius-java-example"))

    // Kafka dependencies
    implementation(libs.kafka.avro.serializer)
    implementation(libs.kafka.clients)

    // Logging dependencies
    implementation(libs.slf4j.api)
    runtimeOnly(libs.slf4j.simple)
}

java {
    toolchain {
        languageVersion = JavaLanguageVersion.of(21)
    }
}

application {
    mainClass = "com.aureliusenterprise.producer.App"
}

tasks.named<Test>("test") {
    useJUnitPlatform()
}

allprojects {
    apply {
        plugin("project-report")
    }
}

tasks.register("projectReportAll") {
    allprojects.forEach {
        dependsOn(it.tasks.getAt("projectReport"))
    }

    gradle.includedBuilds.forEach {
        dependsOn(it.task(":projectReportAll"))
    }
}

tasks.register("e2e") {
    group = "verification"
    nx {
        array("dependsOn", "decrypt", "docker-build")
        set("executor", "@nxlv/python:run-commands")
        set("metadata") {
            set("description", "Run the end-to-end tests for this application")
        }
        set("options") {
            set("command", "uv run pytest e2e")
            set("cwd", "{projectRoot}")
        }
    }
}
