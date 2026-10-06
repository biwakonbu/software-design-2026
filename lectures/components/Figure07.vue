<script setup>
import "../styles/learning-course.css"
import diagrams from "../data/figures07.json"
defineProps({index:Number})
</script>
<template><CourseDiagram :diagram="diagrams[index]" :uid="`lesson07-${index}`" /></template>
