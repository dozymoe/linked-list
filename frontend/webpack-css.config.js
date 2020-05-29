const path = require('path');
const webpack = require('webpack');
const MiniCssExtractPlugin = require('mini-css-extract-plugin');
const OptimizeCssAssetsPlugin = require('optimize-css-assets-webpack-plugin');
const ManifestPlugin = require('webpack-manifest-plugin');

const autoprefixer = require('autoprefixer');
const noop = require('noop-webpack-plugin');

const isDevelopment = process.env.NODE_ENV !== 'production';
process.traceDeprecation = true;


module.exports = {
    entry: {
        main: [path.resolve(__dirname, 'index.scss')],
    },
    output: {
        path: path.resolve(__dirname, '../public'),
        publicPath: '/',
        filename: 'assets/css/[name].js',
    },
    plugins: [
        new MiniCssExtractPlugin({
            publicPath: '/',
            filename: 'assets/css/[chunkhash].css',
        }),
        isDevelopment ? noop() : new OptimizeCssAssetsPlugin({
            cssProcessor: require('cssnano'),
            cssProcessorPluginOptions: {
                preset: [
                    'default',
                    {
                        discardComments: {
                            removeAll: true,
                        },
                    }
                ],
            },
            canPrint: true,
        }),
        new ManifestPlugin({
            fileName: path.resolve(__dirname, '../var/webpack-css-meta.json'),
            filter: (f) =>
                {
                    return f.name.endsWith('.css');
                },
            sort: (a, b) =>
                {
                    let splita = a.name.split('~');
                    let splitb = b.name.split('~');
                    return splitb.length - splita.length;
                },
        }),
    ],
    module: {
        rules: [
            {
                test: /\.s[ac]ss$/,
                use: [
                    MiniCssExtractPlugin.loader,
                    {
                        loader: 'css-loader',
                        options: {
                            sourceMap: isDevelopment,
                            url: false,
                        },
                    },
                    {
                        loader: 'postcss-loader',
                        options: { plugins: [autoprefixer()] },
                    },
                    'resolve-url-loader',
                    {
                        loader: 'sass-loader',
                        options: {
                            implementation: require('sass'),
                            sourceMap: isDevelopment,
                            sassOptions: {
                                includePaths: ['../node_modules'],
                            },
                        },
                    },
                ],
            },
            {
                test: /\.css$/,
                use: [
                    MiniCssExtractPlugin.loader,
                    {
                        loader: 'css-loader',
                        options: { sourceMap: isDevelopment },
                    },
                    'resolve-url-loader',
                ],
            },
        ],
    },
    optimization: {
        splitChunks: {
            chunks: 'all',
            maxInitialRequests: Infinity,
            maxSize: 500000,
            cacheGroups: {
                base: {
                    name: 'base',
                    test: /[\\/]node_modules[\\/]/,
                },
            },
        },
    },
};
