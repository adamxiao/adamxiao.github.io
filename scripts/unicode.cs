
public class UTF8
{
    /// <summary>
    /// 计算utf-8编码后的字节数
    /// </summary>
    /// <param name="code">Unicode</param>
    /// <returns>utf-8编码后的字节数</returns>
    public static int GetByteCount(int code)
    {
        int i = 1;
        for (int c = code; c > 0x7f; c >>= 6, i++) ;

        return i;
    }

    /// <summary>
    /// 根据utf-8编码的第一个字节计算utf-8编码的字节数
    /// </summary>
    /// <param name="b">utf-8编码的第一个字节</param>
    /// <returns>utf-8编码的字节数</returns>
    public static int GetByteCount(byte b)
    {
        int i = 0;
        int mask = 0x80;
        for (; (b & mask) > 0; mask >>= 1, i++) ;

        if (i == 0)
        {
            i = 1;
        }

        return i;
    }

    /// <summary>
    /// 将提供的Unicode编码为utf-8字节数组
    /// </summary>
    /// <param name="code">Unicode</param>
    /// <returns>utf-8编码的字节数组</returns>
    public static byte[] Encode(int code)
    {
        int len = GetByteCount(code);
        var bytes = new byte[len];

        int c = code;
        for (int i = len - 1; i > 0; i--)
        {
            bytes[i] = (byte)((c & 0x3F) | 0x80);
            c >>= 6;
        }

        int b = 0x100;
        for (int i = 1; i < len; i++)
        {
            b = (b | (b >> 1));
        }

        bytes[0] = (byte)(b | c);

        return bytes;
    }

    /// <summary>
    /// 根据utf-8编码字节数组解码为Unicode
    /// </summary>
    /// <param name="bytes">utf-8编码的字节数组</param>
    /// <returns>对应的Unicode</returns>
    public static int Decode(byte[] bytes)
    {
        int len = GetByteCount(bytes[0]);

        if (len == 1)
        {
            return bytes[0];
        }

        byte mask = 1;
        for (int i = len + 1; i < 8; i++)
        {
            mask = (byte)((mask << 1) | 0x1);
        }

        int code = bytes[0] & mask;
        for (int i = 1; i < len; i++)
        {
            code = code << 6 | (0x7f & bytes[i]);
        }

        return code;
    }
}
