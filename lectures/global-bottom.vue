<template>
  <div class="sd-footer" :class="{ 'sd-footer-cover': $slidev.nav.currentPage === 1 }">
    <span>SOFTWARE DESIGN 2026</span>
    <span>{{ $slidev.nav.currentPage }} / {{ $slidev.nav.total }}</span>
  </div>
</template>
