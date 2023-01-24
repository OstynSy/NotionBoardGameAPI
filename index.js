import express from 'express';
import { Client } from '@notionhq/client';
import * as dotenv from 'dotenv';
dotenv.config();
// Convert xml to json---------------------------
// var parser = require('xml2json');

// var xml = "<foo attr=\"value\">bar</foo>";
// var json = parser.toJson(xml);
// console.log("to json -> %s", json);
// ---------------------------------------------

const notion = new Client({ auth: process.env.NOTION_KEY });
const databaseId = process.env.NOTION_DATABASE_ID;

// search for empty collections
// limit with "-" before searching url
// grab name search BGG for ID

const gameTitle = '7-wonders';
const url = 'https://api.geekdo.com/xmlapi/search?search=' + gameTitle;
async function fetchAsync(url) {
	let response = await fetch(url);
	let data = await response.json();
	return data;
}
console.log(fetchAsync(gameTitle));
//BGG in XML
//

// Search id for other attributes minmax players, time, genre
// populate notion db w info

// const getGames = async () => {
// 	const load = {
// 		path: `databases/${databaseId}/query`,
// 		method: 'POST',
// 	};

// 	const { results } = await notion.request(load);

// 	const games = results.map((page) => {
// 		console.log('START LOG', page.properties.Min_Time.rich_text[0]);
// 		return {
// 			// id: page.id,
// 			// Title: page.properties.Title.title[0],
// 			// Min_Time: page.properties.Min_Time.rich_text[0].type,
// 			// Max_Time: page.properties.Max_Time.rich_text[0],
// 			// Min_Players: page.properties.Min_Players.rich_text[0],
// 			// Max_Players: page.properties.Max_Players.rich_text[0],
// 		};
// 	});
// 	return games;
// };

// (async () => {
// 	const nGames = await getGames();
// 	console.log(nGames);
// })();
