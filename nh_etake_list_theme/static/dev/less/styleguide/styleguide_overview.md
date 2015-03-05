# eTake List Theme Styleguide
This is the styleguide for the eTake List Theme for Patient Flow. The styleguide uses node and npm, once installed you can then use the following to build the styleguide.
 - `npm install`
 - `gulp styleguide`

This will then create the styleguide in it's own folder in the same directory.

## Coding style
- Use hyphens in selector names where possible
- Indent 4 spaces
- One property per line, use shorthand where available
- One line gap between bottom of a style and start of another style
- One line gap between bottom of a property declaration group and next property declaration group
- One Space between selector and brace, one space between color and property value
- Use em for vertical sizing (fonts etc)
- Use percentages for horizontal sizing (width etc)
- Pixels are allowed for borders but use calc to subtract the left and right borders from the desired width
- Declare properties in this order Position, Box Model, Typography, Visual and Misc

The Styleguide build script will run these against Recess, Twitter's LESS linter so coding style must be adherred to.