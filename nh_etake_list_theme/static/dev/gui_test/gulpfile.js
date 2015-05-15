var gulp = require('gulp'),
	coffeelint = require('gulp-coffeelint'),
	docco = require('gulp-docco'),
	coffee = require('gulp-coffee');

gulp.task('compile', function(){
	gulp.src(['src/*.coffee'])
	.pipe(coffeelint())
	.pipe(coffeelint.reporter())
	.pipe(coffee())
	.pipe(gulp.dest('dest'))
});

gulp.task('docs', function(){
	gulp.src(['src/*.coffee'])
	.pipe(docco())
	.pipe(gulp.dest('docs'))
});

gulp.task('move_to_testing', function(){
    gulp.src(['src/*.coffee'])
        .pipe(coffeelint())
        .pipe(coffeelint.reporter())
        .pipe(coffee())
        .pipe(gulp.dest('../.. /../../src/gui_test'))
})

gulp.task('default', ['compile', 'docs', 'move_to_testing']);
