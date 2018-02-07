'use strict';

const gulp            = require('gulp');
const header          = require('gulp-header');
const uglify          = require('gulp-uglify');
const rename          = require('gulp-rename');
const pkg             = require('./package.json');

const banner = ['/*!',
  ' * <%= pkg.name %> <%= pkg.version %>',
  ' * <%= pkg.description %>',
  ' *',
  ' * <%= pkg.homepage %>',
  ' * @license <%= pkg.license %>',
  ' */',
  '',
  ''].join('\n');

gulp.task('scripts', () => {
  return gulp.src(['src/*.js'])
    .pipe(header(banner, { pkg: pkg }))
    .pipe(gulp.dest('dist'))
    .pipe(uglify())
    .pipe(header(banner, { pkg: pkg }))
    .pipe(rename({ suffix: '.min', extname: '.js' }))
    .pipe(gulp.dest('dist'))
});

gulp.task('watch', () => {
  gulp.watch(['src/*.js'], ['scripts']);
});

gulp.task('default', ['scripts', 'watch']);