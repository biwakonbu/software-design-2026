<script setup>
import "../styles/learning-course.css"
import diagrams from "../data/figures08.json"
defineProps({index:Number})
</script>
<template><CourseDiagram :diagram="diagrams[index]" :uid="`lesson08-${index}`" /></template>
