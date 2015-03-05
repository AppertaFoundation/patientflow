var gulp = require('gulp'),
	less = require('gulp-less'),
	kss = require('gulp-kss'),
	csslint = require('gulp-csslint'),
	recess = require("gulp-recess"),
	minifycss = require('gulp-minify-css'),
	uncss = require('gulp-uncss'),
	notify = require('gulp-notify'),
	util = require('gulp-util'),
	path = require('path');
	del = require('del'),
	glob = require('glob');
	
gulp.task('styleguide', function(){
	del(['styleguide/**']);
	gulp.src(['style.less', 'components/*.less'])
	.pipe(recess())
	.pipe(kss({
		overview: 'styleguide_overview.md'
	}))
	.pipe(gulp.dest('styleguide/'));
	
});
	
gulp.task('compileLESS', function(){
	gulp.src('style.less')
	.pipe(less())
	.pipe(csslint())
	.pipe(gulp.dest('styleguide/public/'));
});

gulp.task('polishCSS', function(){
	gulp.src('styleguide/public/style.css')
	.pipe(uncss({
		html: glob.sync('styleguide/**/*.html')
	}))
	.pipe(minifycss({
		keepSpecialComments: 0,
		keepBreaks: false 
	}))
	.pipe(gulp.dest('styleguide/public/'));
});	


gulp.task('build', ['styleguide', 'compileLESS', 'polishCSS']);