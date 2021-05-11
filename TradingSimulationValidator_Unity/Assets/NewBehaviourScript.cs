using System;
using System.Collections;
using System.Collections.Generic;
using System.IO;
using UnityEngine;
using UnityEngine.UI;

public class NewBehaviourScript : MonoBehaviour
{
    public Text outPutText;
    public Toggle recordToggle;
    public Slider valueSilder;
    public InputField recordFileInputField;
    public float initCash = 1000;
    public float loss = -0.1f;
    public float gran = 0.05f;
    float lastValue = -1;
    Vector2 positionToCash = Vector2.zero;

    DateTime startTime;
    Hashtable recordJson = new Hashtable();
    bool usingRecordFile = false;

    List<Hashtable> recordValues = new List<Hashtable>();



    // Start is called before the first frame update
    void Start()
    {
        valueSilder.onValueChanged.AddListener(ValueChange);
    }

    // Update is called once per frame
    void Update()
    {
        
    }

    public void StartReadRecordFile()
    {
        if (!File.Exists(recordFileInputField.text))
        {
            outPutText.text = "文件不存在：" + recordFileInputField.text;
            return;
        }

        recordToggle.isOn = false;
        recordToggle.interactable = false;
        recordFileInputField.interactable = false;
        valueSilder.interactable = false;
        recordJson = MiniJSON.jsonDecode(File.ReadAllText(recordFileInputField.text)) as Hashtable;
        StopAllCoroutines();
        StartCoroutine(RunningRecordFileValues(recordJson));
    }

    /// <summary>
    /// 创建仓位
    /// </summary>
    public float CreatePosition()
    {

        return 1000;
    }

    void ValueChange(float value)
    {
        if (!recordJson.ContainsKey("startTime"))
        {
            startTime = DateTime.Now;
            recordToggle.interactable = false;
            recordJson.Add("startTime", DateTime.Now.ToString("yyyy'-'MM'-'dd'T'HH'-'mm'-'ss"));
            Debug.Log("startTime = " + (DateTime.Now - startTime).Ticks);
        }

        if (!usingRecordFile && recordToggle.isOn)
        {
            recordValues.Add(new Hashtable { { "time", (DateTime.Now - startTime).Ticks }, { "value", value } });
            Debug.Log("time = " + (DateTime.Now - startTime).Ticks + "\tvalue = " + value);
        }

        float all = initCash;
        if (positionToCash[0] == 0)
        {
            positionToCash[0] = all / 2 / value;
            positionToCash[1] = all / 2;
        }
        else if (value * positionToCash[0] < positionToCash[1] * 0.9f)
        {
            all = value * positionToCash[0] + positionToCash[1];
            positionToCash[0] = all / 2 / value;
            positionToCash[1] = all / 2;
        }
        else if (value * positionToCash[0] > positionToCash[1] * 1.05f)
        {
            all = value * positionToCash[0] + positionToCash[1];
            positionToCash[0] = all / 2 / value;
            positionToCash[1] = all / 2;
        }
        string line = "value = " + value + " -> (" + positionToCash[0] + "," + positionToCash[1] + ")" + (positionToCash[0] * value + positionToCash[1]);
        outPutText.text = line + "\n" + outPutText.text;
        Debug.Log(line);
    }

    public IEnumerator RunningRecordFileValues(Hashtable recordJson)
    {
        ArrayList recordValues2 = null;
        if (recordJson.ContainsKey("recordValues"))
        {
            recordValues2 = recordJson["recordValues"] as ArrayList;
            Debug.Log(recordValues2.ToArray());
            Debug.Log((recordValues2[0] as Hashtable)["time"]);
        }
        usingRecordFile = true;
        yield return null;
        long lastTime = 0;
        for (int i = 0; i < recordValues2.Count; i++)
        {
            long time = (long)(double)(recordValues2[i] as Hashtable)["time"];
            yield return new WaitForSeconds((time - lastTime) / 10000000f);
            valueSilder.value = (float)(double)(recordValues2[i] as Hashtable)["value"];
            lastTime = time;
        }

        recordToggle.interactable = true;
        recordFileInputField.interactable = true;
        valueSilder.interactable = true;
    }

    private void OnDestroy()
    {
        if (usingRecordFile)
        {
            return;
        }

        recordJson.Add("recordValues", recordValues.ToArray());

        string filePath = recordJson["startTime"] + ".json";
        filePath = Directory.GetParent(Application.dataPath).FullName + Path.DirectorySeparatorChar + filePath;

        File.WriteAllText(filePath, MiniJSON.jsonEncode(recordJson));


        Debug.Log("OnDestroy\n" + filePath + "\n" + MiniJSON.jsonEncode(recordJson));
    }
}
