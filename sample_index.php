<html>
<head>
<title>English Method</title>
</head>
<body>

<table border=1 width=100%>
	<tr>
		<td valign=top width=100>
			<u>Known words:</u>
			<br><br>
			<table width=100%>
				<?php
				$arquivo = fopen('stopwords.txt','r');
				while(!feof($arquivo)) {
					$linha = fgets($arquivo);
					echo "<tr>";
					echo "<td>" . $linha . "</td>";
					echo "</tr>";
				}
				fclose($arquivo);
				?>
			</table>
		</td>
		<td valign=top width=400>
			<u>Suggestions for study:</u>
			<br><br>
			<table width=100%>
				<?php
				$arquivo = fopen('output.json','r');
				$content = "no content";
				$title = $_GET['title'];
				while(!feof($arquivo)) {
					$linha = fgets($arquivo);
					$data_line = json_decode($linha);
					if ($data_line) {
						if (strpos($data_line->{'title'}, $title) !== false) {
							echo "<b><u>" . $data_line->{'title'} . "</u></b><br><br>";
							$content = $data_line;
							break;
						} 
					}
				}
				fclose($arquivo);
				foreach ($content->{'examples'} as $item) {
					echo "<tr>";
					echo "<td> < <b>" . $item->{'term'} . "</b></td>";
					echo "<td align=right>";
					echo "[TFIDF: " . $item->{'tfidf'} . "] [FREQ: " . $item->{'freq'} . "] ";
					echo "<a href='https://www.bing.com/images/search?q=" . str_replace("_", "+", $item->{'term'}) . "' target=infoframe>Images</a> | ";
					echo "<a href='http://www.bing.com/translate' target=infoframe>Translate</a>";
					echo "</td>";
					echo "</tr>";
					echo "<tr>";
					echo "<td colspan=2>";
					$counter = 1;
					foreach ($item->{'phrases'} as $phrase) {
						echo "<font size=2>";
						echo "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;";
						echo $counter . ". ". $phrase;
						$counter += 1;
						echo "</font>";
						echo "<br>";
					}
					echo "<br>";
					echo "</td>";
					echo "</tr>";
				}


				// $examples = array();
				// $selected_term = $_GET['term'];
				// while(!feof($arquivo)) {
				// 	$linha = fgets($arquivo);
				// 	$data_line = json_decode($linha);
				// 	if ($data_line) {
				// 		echo "<tr>";
				// 		echo "<td> < <b>" . $data_line->{'term'} . "</b></td>";
				// 		echo "<td align=right>";
				// 		echo "[TFIDF: " . $data_line->{'tfidf'} . "] [FREQ: " . $data_line->{'freq'} . "] ";
				// 		// echo "<a href='http://images.google.com/search?tbm=isch&q=" . str_replace("_", "+", $data_line->{'term'}) . "' target=infoframe>Images</a> | ";
				// 		echo "<a href='https://www.bing.com/images/search?q=" . str_replace("_", "+", $data_line->{'term'}) . "' target=infoframe>Images</a> | ";
				// 		// echo "<a href='https://translate.google.com.br/#auto/pt/" . str_replace("_", "+", $data_line->{'term'}) . "' target=blank>Translate</a>";
				// 		echo "<a href='http://www.bing.com/translate' target=infoframe>Translate</a>";
				// 		echo "</td>";
				// 		echo "</tr>";
				// 		echo "<tr>";
				// 		echo "<td colspan=2>";
				// 		$counter = 1;
				// 		foreach ($data_line->{'examples'} as $item) {
				// 			echo "<font size=2>";
				// 			echo "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;";
				// 			echo $counter . ". ". $item;
				// 			$counter += 1;
				// 			echo "</font>";
				// 			echo "<br>";
				// 		}
				// 		echo "<br>";
				// 		echo "</td>";
				// 		echo "</tr>";
				// 		if ($selected_term == $data_line->{'term'}) {
				// 			$examples = $data_line->{'examples'};
				// 		}
				// 	}
				// }
				// fclose($arquivo);
				?>
			</table>
		</td>
		<td valign=top width=500>
			<u>Extra info:</u>
			<br><br>
			<iframe id="infoframe" name="infoframe" src="https://www.bing.com/images/search?q=chilli" height="100%" width="100%" frameborder="1" scrolling="yes"></iframe>
		</td>		
	</tr>
</table>

</body>
</html>
