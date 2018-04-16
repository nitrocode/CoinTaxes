# TODO

## Hard

- [ ] Add all currency pairs with an option for specific ones
- [ ] If transactions go over 8949, use SCHEDULE D-1 continuation sheet

## Moderate

- [ ] Add Gemini
- [ ] Add Poloniex
- [ ] Add Bittrex - currently uses a csv file, seems possible with the api
    * [/account/getorderhistory](https://support.bittrex.com/hc/en-us/articles/115003723911#apireference)
- [ ] Python3 compatibility

# Easy

- [ ] Package up app to a pip package
- [ ] Add `CONTRIBUTING.md`
- [ ] Add `LICENSE`

## Done

- [x] Convert credentials to yaml
- [x] Make the app os agnostic - particularly with paths
- [x] Put all output files in an output directory
- [x] Structure coinbase and gdax into `exchanges` package (if necessary)
- [x] Structure 8949 and turbotax into `formats` package (if necessary)
- [x] Structure stock pdfs into `forms` package
