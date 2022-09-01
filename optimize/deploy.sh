#
# User input
#
# export client_id="66061455128-2lpvm8j8faqdhc8tqt5f1uf4sqspk033.apps.googleusercontent.com"
# export client_secret="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"
# export spreadsheet_id="16Xxl754P2D33Ca1fEZzIDmlooJSCwN-XOUeWMsJWEcs"
# export ads_developer_token="z27QEhvZe2mjjYFmwwfskg"
# export ads_mcc_id="3172025529"
# export gcp_read_project="google.com:robsantos-agamotto"
# export gcp_read_dataset="horus_info"
# export gcp_write_project="google.com:robsantos-agamotto"
# export gcp_write_dataset="horus_info"



echo "Enter your OAuth Client Id: "
read client_id

echo "Enter your OAuth Client Secret: "
read client_secret


#
# generate_token.py
#
# export access_token="ya29.A0AVA9y1vsmMbj4rkj7oK5WOQ8Pnsh46Aozy3v0z2f3pkHEDRq7V82TzK6fdAg5Z-W10NXq6tVdeXMI3JOZ5Kj1sYQjfcPd4AEcUQkpj--CwUhlJsbkmnqQ_uZJw54XNJSj_9_D6jbJaWg9ZLAaiMlanWeyRG7aCgYKATASATASFQE65dr8mtuZ8yVPJ36yX2z2ftLkzw0163"
# export refresh_token="1//0hrT7w78FUrCGCgYIARAAGBESNwF-L9IrpKFgnCTU7H1jaWDzjnIbHC0XNJ-TG0sVePOvA4ZIIqqlm5aQtxoQq98iyo63GsVpW4Y"
# 
# #
# # create google-ads.yaml file?
# #
# 
# 
# rm -f agamotto.yaml
# ( echo "cat <<EOF >agamotto.yaml";
#   cat templates/agamotto.yaml;
# ) >temp.yml
# . temp.yml
