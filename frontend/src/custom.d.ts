/// <reference types="vite/client" />

// Allow importing CSS/SCSS and common static assets from TypeScript files
declare module '*.css'
declare module '*.scss'
declare module '*.sass'
declare module '*.less'
declare module '*.styl'

declare module '*.png'
declare module '*.jpg'
declare module '*.jpeg'
declare module '*.gif'
declare module '*.webp'

declare module '*.svg' {
  const content: any
  export default content
}
