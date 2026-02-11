plugins {
    // Apply the foojay-resolver plugin to allow automatic download of JDKs
    id("org.gradle.toolchains.foojay-resolver-convention") version "1.0.0"
}

include("aurelius-java-producer-example")
project(":aurelius-java-producer-example").projectDir = file("apps/aurelius-java-producer-example")

include("aurelius-java-example")
project(":aurelius-java-example").projectDir = file("libs/java/aurelius-java-example")
