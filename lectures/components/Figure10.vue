<script setup>
import "../styles/learning-course.css"
import diagrams from "../data/figures10.json"
defineProps({index:Number})
</script>
<template><CourseDiagram :diagram="diagrams[index]" :uid="`lesson10-${index}`" /></template>
