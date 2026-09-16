import dev.nx.gradle.nx
import java.io.File

nx {
    set("name", "aurelius-java-producer-example")
    array("implicitDependencies", "aurelius-dev-kafka")
}

plugins {
    application
    id("jacoco")
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

    // Other dependencies
    implementation(libs.jackson.core)
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
    finalizedBy(tasks.named("jacocoTestReport"))
}

/**
 * Loads a .env file and returns key-value pairs as a map.
 * Skips blank lines, comments, and handles surrounding quotes.
 */
fun loadEnv(file: File): Map<String, String> {
    val env = mutableMapOf<String, String>()
    if (!file.exists()) return env
    file.forEachLine { line ->
        val trimmed = line.trim()
        if (trimmed.isEmpty() || trimmed.startsWith("#")) return@forEachLine
        val parts = trimmed.split("=", limit = 2)
        if (parts.size < 2) return@forEachLine
        val key = parts[0].trim()
        var value = parts[1].trim()
        if (value.length >= 2) {
            if ((value.startsWith("\"") && value.endsWith("\"")) ||
                (value.startsWith("'") && value.endsWith("'"))) {
                value = value.substring(1, value.length - 1)
            }
        }
        env[key] = value
    }
    return env
}

// Inject .env values into the 'run' task's process environment
tasks.named("run", JavaExec::class).configure {
    val envFile = project.file("${projectDir}/.env")
    environment(loadEnv(envFile))
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
        array("dependsOn") {
            add("decrypt")
            add("docker-build")
            obj {
                set("target", "up")
                set("dependencies", true)
            }
        }
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

tasks.register("sonar") {
    nx {
        array("dependsOn", "decrypt", "build")
        set("command", "sonar-scanner -Dproject.settings={projectRoot}/sonar-project.properties -Dsonar.working.directory={projectRoot}/.scannerwork")
        set("metadata") {
            set("description", "Run SonarQube analysis on the project")
        }
    }
}

tasks.jacocoTestReport {
    group = "verification"
    description = "Run JaCoCo code coverage report for the test task"

    reports {
        xml.required.set(true)
        html.required.set(false)
        csv.required.set(false)
    }
}
