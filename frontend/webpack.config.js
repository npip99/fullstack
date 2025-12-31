import CopyPlugin from 'copy-webpack-plugin';
import HtmlWebpackPlugin from 'html-webpack-plugin';
import path from 'path';

const __dirname = import.meta.dirname;

export default (env, argv) => ({
  entry: './src/index.tsx',
  output: {
    path: path.resolve(__dirname, '../frontend-build'),
    filename: 'bundle.js',
  },
  devtool: argv.mode === 'production' ? false : 'eval-source-map',
  performance:
    argv.mode === 'production'
      ? {
          maxAssetSize: 1000000,
          maxEntrypointSize: 1000000,
          hints: 'error',
        }
      : false,
  module: {
    rules: [
      {
        test: /\.(ts|tsx)$/,
        exclude: /node_modules/,
        use: 'babel-loader',
      },
      {
        test: /\.css$/,
        use: ['style-loader', 'css-loader', 'postcss-loader'],
      },
    ],
  },
  resolve: {
    extensions: ['.tsx', '.ts', '.js'],
  },
  plugins: [
    new HtmlWebpackPlugin({
      template: './public/index.html',
    }),
    new CopyPlugin({
      patterns: [
        {
          from: 'assets',
          to: 'assets',
        },
      ],
    }),
  ],
  devServer: {
    static: {
      directory: path.join(__dirname, '../frontend-build'),
    },
    port: 8088,
    historyApiFallback: true,
    hot: true,
    proxy: [
      {
        context: ['/api'],
        target: 'http://localhost:8080',
      },
    ],
  },
});
