using System;
using System.Collections.Generic;
using System.Linq;
using System.IO;
using System.Threading.Tasks;

namespace MapCalculate
{
    public class Map
    {
        public int ncols;
        public int nrows;
        public double x;
        public double y;
        public float cell_size;
        public string no_data;
        public List<List<string>> data = null;
        public Dictionary<string, int> crossed = null;
        public Map(Map map)
        {
            this.ncols = map.ncols;
            this.nrows = map.nrows;
            this.x = map.x;
            this.y = map.y;
            this.cell_size = map.cell_size;
            this.no_data = map.no_data;
            this.data = new List<List<string>>();
            for (int i = 0; i < map.data.Count; i++)
            {
                this.data.Add(new List<string>());
                for (int j = 0; j < map.data[i].Count; j++)
                {
                    this.data[i].Add(null);
                }
            }
        }
        public Map(string file)
        {
            String[] content = File.ReadAllLines(file);
            string[] temp;
            for (int i = 0; i < 6; i++)
            {
                temp = content[i].Split(new[] { ' ' }, StringSplitOptions.RemoveEmptyEntries);
                if (temp[0].Contains("col"))
                    this.ncols = Int32.Parse(temp[1]);
                if (temp[0].Contains("row"))
                    this.nrows = Int32.Parse(temp[1]);
                if (temp[0].Contains("x"))
                    this.x = Double.Parse(temp[1]);
                if (temp[0].Contains("y"))
                    this.y = Double.Parse(temp[1]);
                if (temp[0].Contains("cell"))
                    this.cell_size = float.Parse(temp[1]);
                if (temp[0].ToLower().Contains("no"))
                    this.no_data = temp[1];
            }
            this.data = new List<List<string>>();
            for (int i = 6; i < content.Length; i++)
            {
                this.data.Add(null);
            }
            Parallel.For(6, content.Length, i => this.data[i - 6] = (content[i].Split(new[] { ' ' }, StringSplitOptions.RemoveEmptyEntries).ToList()));
        }
        public Map lookup(string[] code, string[] value)
        {
            Map result = new Map(this);
            bool crl;
            for(int i=0;i<data.Count;i++)
            {
                for(int j=0;j<data[i].Count;j++)
                {
                    if (data[i][j] == no_data)
                        result.data[i][j] = no_data;
                    else
                    {
                        crl = true;
                        for (int k = 0; k < code.Length; k++)
                        {
                            if (data[i][j] == code[k])
                            {
                                result.data[i][j]=value[k];
                                crl = false;
                                break;
                            }
                        }
                        if (crl)
                            result.data[i][j] = data[i][j];
                    }
                }
            }
            return result;
        }
        public Map intersect(Map map)
        {
            if (x != map.x || y != map.y)
                throw new System.ArgumentException("Maps are not in same position");
            if (ncols != map.ncols || nrows != map.nrows || cell_size != map.cell_size)
                throw new System.ArgumentException("Maps dont have same size");
            Dictionary<string, int> dict = new Dictionary<string, int>();
            int k = 1;
            Map result = new Map(this);
            for (int i = 0; i < data.Count; i++)
            {
                for (int j = 0; j < data[i].Count; j++)
                {
                    if (data[i][j] != no_data && map.data[i][j] != map.no_data)
                    {
                        if (!dict.ContainsKey(data[i][j] + "," + map.data[i][j]))
                        {
                            dict.Add(data[i][j] + "," + map.data[i][j], k);
                            k++;
                        }
                        result.data[i][j] = dict[data[i][j] + "," + map.data[i][j]].ToString();
                    }
                    else
                        result.data[i][j] = result.no_data;
                }
            }
            result.crossed = dict;
            return result;
        }
        public Dictionary<string, int> intersect_count(Map map)
        {
            if (x != map.x || y != map.y)
                throw new System.ArgumentException("Maps are not in same position");
            if (ncols != map.ncols || nrows != map.nrows || cell_size != map.cell_size)
                throw new System.ArgumentException("Maps dont have same size");

            Dictionary<string, int> dict = new Dictionary<string, int>();
            for (int i = 0; i < data.Count; i++)
            {
                for (int j = 0; j < data[i].Count; j++)
                {
                    if (data[i][j] != no_data && map.data[i][j] != map.no_data)
                    {
                        if (!dict.ContainsKey(data[i][j] + "," + map.data[i][j]))
                        {
                            dict.Add(data[i][j] + "," + map.data[i][j], 0);
                        }
                        dict[data[i][j] + "," + map.data[i][j]] += 1;
                    }
                }
            }
            return dict;
        }
        public Dictionary<string,int> count()
        {
            var dict = new Dictionary<string,int>();
            for (int i = 0; i < data.Count; i++)
            {
                for (int j = 0; j < data[i].Count; j++)
                {
                    if (data[i][j] != no_data)
                    {
                        if(!dict.ContainsKey(data[i][j]))
                        {
                            dict.Add(data[i][j], 0);
                        }
                        dict[data[i][j]] += 1;
                    }
                }
            }
            return dict;
        }
        public int area()
        {
            int result = 0;
            for(int i=0;i<data.Count;i++)
            {
                for(int j=0;j<data[i].Count;j++)
                {
                    if(data[i][j]!=no_data)
                    {
                        result++;
                    }
                }
            }
            return result;
        }
        public double lat()
        {
            double K0 = 0.9996;

            double E = 0.00669438;
            double E2 = E * E;
            double E3 = E2 * E;
            double E_P2 = E / (1.0 - E);

            double SQRT_E = Math.Sqrt(1 - E);
            double _E = (1 - SQRT_E) / (1 + SQRT_E);
            double _E2 = _E * _E;
            double _E3 = _E2 * _E;
            double _E4 = _E3 * _E;
            double _E5 = _E4 * _E;

            double M1 = (1 - E / 4 - 3 * E2 / 64 - 5 * E3 / 256);
            double M2 = (3 * E / 8 + 3 * E2 / 32 + 45 * E3 / 1024);
            double M3 = (15 * E2 / 256 + 45 * E3 / 1024);
            double M4 = (35 * E3 / 3072);

            double P2 = (3.0 / 2 * _E - 27.0 / 32 * _E3 + 269.0 / 512 * _E5);
            double P3 = (21.0 / 16 * _E2 - 55.0 / 32 * _E4);
            double P4 = (151.0 / 96 * _E3 - 417.0 / 128 * _E5);
            double P5 = (1097.0 / 512 * _E4);

            int R = 6378137;
            double x = this.x - 500000;
            double y = this.y;
            double m = y / K0;

            double mu = m / (R * M1);

            double p_rad = (mu +
                    P2 * Math.Sin(2 * mu) +
                    P3 * Math.Sin(4 * mu) +
                    P4 * Math.Sin(6 * mu) +
                    P5 * Math.Sin(8 * mu));

            double p_sin = Math.Sin(p_rad);
            double p_sin2 = p_sin * p_sin;

            double p_cos = Math.Cos(p_rad);

            double p_tan = p_sin / p_cos;
            double p_tan2 = p_tan * p_tan;
            double p_tan4 = p_tan2 * p_tan2;

            double ep_sin = 1 - E * p_sin2;
            double ep_sin_sqrt = Math.Sqrt(1 - E * p_sin2);

            double n = R / ep_sin_sqrt;
            double r = (1 - E) / ep_sin;

            double c = _E * p_cos * p_cos;
            double c2 = c * c;

            double d = x / (n * K0);
            double d2 = d * d;
            double d3 = d2 * d;
            double d4 = d3 * d;
            double d5 = d4 * d;
            double d6 = d5 * d;

            double latitude = (p_rad - (p_tan / r) *
                        (d2 / 2 -
                        d4 / 24 * (5 + 3 * p_tan2 + 10 * c - 4 * c2 - 9 * E_P2)) +
                        d6 / 720 * (61 + 90 * p_tan2 + 298 * c + 45 * p_tan4 - 252 * E_P2 - 3 * c2));
            return latitude;
        }
        public void toMap(string file)
        {
            String content = "";
            content = content + "ncols         " + ncols.ToString();
            content = content + System.Environment.NewLine;
            content = content + "nrows         " + nrows.ToString();
            content = content + System.Environment.NewLine;
            content = content + "xllcorner     " + x.ToString();
            content = content + System.Environment.NewLine;
            content = content + "yllcorner     " + y.ToString();
            content = content + System.Environment.NewLine;
            content = content + "cellsize      " + cell_size.ToString();
            content = content + System.Environment.NewLine;
            content = content + "NODATA_value  " + no_data.ToString();
            content = content + System.Environment.NewLine;
            File.WriteAllText(file, content);
            for (int i = 0; i < data.Count; i++)
            {
                content = "";
                for (int j = 0; j < data[i].Count; j++)
                {
                    content = content + data[i][j] + ' ';
                }
                content = content + System.Environment.NewLine;
                File.AppendAllText(file, content);
            }
        }
        static public List<List<string>> readFile(string file)
        {
            List<List<string>> lls = new List<List<string>>();
            using (StreamReader sr = new StreamReader(file))
            {
                string strLine = String.Empty;
                strLine = sr.ReadLine();
                string[] temp;
                temp=strLine.Split(new[] { '\t' }, StringSplitOptions.RemoveEmptyEntries);

                for(int j=0;j<temp.Length;j++)
                {
                    lls.Add(new List<string>());
                    lls[j].Add(temp[j]);
                }
                while (true)
                {
                    strLine = sr.ReadLine();
                    if (strLine == null)
                        break;
                    temp = strLine.Split(new[] { '\t' }, StringSplitOptions.RemoveEmptyEntries);
                    for (int j = 0; j < temp.Length; j++)
                    {
                        lls[j].Add(temp[j]);
                    }
                }
            }
            return lls;
        }
        static public void writeFile(string file, string line, bool append)
        {
            line = line + System.Environment.NewLine;
            if (append)
                File.AppendAllText(file, line);
            else
                File.WriteAllText(file, line);
        }
    }
}
