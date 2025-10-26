/// <reference types="react-scripts" />

// CSS Modules type declaration
declare module '*.module.css' {
  const classes: { [key: string]: string };
  export default classes;
}
