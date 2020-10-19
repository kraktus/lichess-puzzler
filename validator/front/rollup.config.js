const resolve = require('@rollup/plugin-node-resolve').default;
const commonjs = require('@rollup/plugin-commonjs');
const typescript = require('@rollup/plugin-typescript');
// const terser = require('rollup-plugin-terser').terser;

export default (args) => {
  const prod = args['config-prod'];
  const name = 'PuzzleValidator';
  return {
    input: 'src/main.ts',
    output: [
      prod ? {
        file: '../back/public/dist/puzzle-validator.min.js',
        format: 'iife',
        name: name,
        plugins: [
          // terser({
          //   safari10: false,
          //   output: {
          //     comments: false,
          //   },
          // }),
        ],
      } : {
        file: '../back/public/dist/puzzle-validator.dev.js',
        format: 'iife',
        name: name,
      }
    ],
    plugins: [
      resolve(),
      typescript(),
      commonjs({
        extensions: ['.js', '.ts'],
      }),
    ],
  };
};
