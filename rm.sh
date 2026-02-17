if [ -z $1 ]; then
	echo "set a file"
else
	echo "wiping data..."
	echo '\x02' > $1
	echo '\x04' > $1
	echo '\xff' > $1
	echo '\x00' > $1
	echo '\x02' > $1
	echo '\x02' > $1
	echo '\x01' > $1
	echo '\x34' > $1
	echo '\x02' > $1
	echo '\xf2' > $1
	echo '\x02' > $1
	echo '\x0f' > $1
	echo '\xfff' > $1
	echo '\x02' > $1
	echo '\x02f' > $1
	echo '\x001' > $1
	echo '\x0f0' > $1
	echo '\x02' > $1
	echo '\x01' > $1
	echo '\x34' > $1
	echo '\x02' > $1
	echo '\xf2' > $1
	echo '\x02' > $1
	echo '\x00' > $1
	echo '\x00' > $1
	echo '\x00' > $1
	echo '\x00' > $1
	echo '\x00' > $1
	echo '\x00' > $1
	echo '\x00' > $1
	echo '\x00' > $1
	echo '\x00' > $1
	echo '\x00' > $1
	echo '\x00' > $1
	echo '\x00' >> $1
	echo '\x00' >> $1
	echo '\x00' >> $1
	echo '\x00' >> $1
	echo '\x00' >> $1
	echo '\x00' >> $1
	echo '\x00' >> $1
	echo '\x00' >> $1
	echo '\x00' >> $1
	rm $1
fi
