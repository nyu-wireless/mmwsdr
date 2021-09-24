# COSMOS - Sandbox 1

## General Information

<table>
    <thead>
        <tr>
            <th rowspan=2>Device</th>
            <th colspan=6>Interface</th>
        </tr>
        <tr>
            <th colspan=2>Control</th>
            <th colspan=2>Data1</th>
            <th colspan=2>Data2</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td>N310 (1)</td>
            <td>10.113.6.1</td>
            <td>rfdev3-1</td>
            <td>10.114.6.1</td>
            <td>rfdev3-1a</td>
            <td>10.115.6.1</td>
            <td>rfdev3-1b</td>
        </tr>
    </tbody>
</table>


```bash
<user>@console:~$ ssh -Y root@srv1-in1 -R 5054:am1.cosmos-lab.org:5054
<user>@console:~$ ssh -Y root@srv1-in2 -R 5054:am1.cosmos-lab.org:5054
```

## More Information
The above information has been collected from the COSMOS wiki pages. Please refer to them for more information
and examples.
* [COSMOS Wiki - Sandbox 1](https://wiki.cosmos-lab.org/wiki/Architecture/Domains/cosmos_sb1)
* [COSMOS Wiki - XY Table](https://wiki.cosmos-lab.org/wiki/Resources/Services/XYTable)
