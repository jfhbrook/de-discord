# Data Engineering Discord

## The Rules

See `RULES.md`.

## Emojis

If you would like to add emojis, make a pull request with the emoji images you
want to add in the `./emojis` directory.

The filename is used to set the name of the emoji. For example,
`./emojis/spark.png` would turn into the `:spark:` emoji in Discord.

Any format that pillow supports will work, though all images are currently
normalized into non-animated PNGs (easy to change if you want to make a PR).
Your image should ideally be 128px by 128px, but the CI system will
automatically resize it so don't stress too hard.

If you have imagemagick installed, you can resize raster images with something
like this:

``` bash
convert "$INPUT_IMAGE" -resize 128x128> "$OUTPUT_IMAGE"
```

If you find an svg, you can convert it to raster on MacOS with something like
this:

``` bash
qlmanage -t -s 128 -o . "$INPUT_IMAGE"
mv "${INPUT_IMAGE}.png" "$OUTPUT_IMAGE"
```

Alternately, you can also try:

``` bash
rsvg-convert -h 128 "$INPUT_IMAGE" > "$OUTPUT_IMAGE"
```

Your PR will have basic linting and tests run against it to make sure that code
looks good and that pillow is able to do what it needs to do with the emoji. If
that looks good and the PR gets approved and merged, CI will automatically
configure the emoji in the Discord.

## Setup

This project includes both an `environment.yml` for Conda based workflows and a
`requirements.txt` file for virtualenv/pip based workflows. Conda delegates to
the requirements file. Otherwise, this project's setup is unopinionated with
respect to how Python is installed and managed.

## Tools

In an activated environment, run the `de` command. It should be somewhat
self-documenting. Somewhat.

## License

This code is licensed with an Apache 2.0 license. See the `LICENSE` and `NOTICE`
files for details.
